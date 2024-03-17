from fastapi import FastAPI, HTTPException, Header, Form, Depends, UploadFile, File
from datetime import datetime, date, timedelta
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import config
from hashlib import sha256
from sqlalchemy.orm import Session
import os
from psycopg2.extensions import connection

from authentication import create_jwt_token, verify_jwt_token, verify_user_from_db
from database import get_db

DATABASE_URL = config.DATABASE_URL
SECRET_KEY = config.SECRET_KEY 
ALGORITHM = config.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES= config.ACCESS_TOKEN_EXPIRE_MINUTES

app = FastAPI()

class User(BaseModel):
    username:str
    password:str
    email:str
    birthday:date = None
    last_login:datetime = None
    create_time:datetime = datetime.utcnow()

class Video(BaseModel):
    title: str
    description: str
    video_file: UploadFile


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def update_last_login(username: str, last_login: datetime, db: connection):
    update_query = 'UPDATE public."users" SET "last_login" = %s WHERE "username" = %s'
    cursor = db.cursor()
    cursor.execute(update_query, (last_login, username))
    db.commit()
    cursor.close()
    return {"message": "last_login updated"}

def verify_identity(token: str = Header(..., convert_underscores=True), db: connection = Depends(get_db)):
    payload = verify_jwt_token(token)
    username = payload["username"]
    stored_password = verify_user_from_db(username, db)
    if stored_password is None:
         raise HTTPException(status_code=401, detail="User not found")
    return (True,username)

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...), db: connection = Depends(get_db)):
    stored_password = verify_user_from_db(username, db)
    password_hash = sha256(password.encode('utf-8')).hexdigest()
    if stored_password is None or password_hash != stored_password:
        raise HTTPException(status_code=401, detail="Invalid")
    
    # update last_login
    update_last_login(username, datetime.utcnow(), db)

    # 先verify user 再create token
    jwt_token = create_jwt_token(username)
    return {"username": username, "token": jwt_token}

@app.get("/user/")
def get_username(Authorization:str = Header(...), db: connection = Depends(get_db)):
    result = verify_identity(Authorization, db)
    if result[0]:
        username = result[1]
        query = 'SELECT * FROM public."users" WHERE "username" = %s'
        cursor = db.cursor()
        cursor.execute(query, (username,))

        row = cursor.fetchone()
        cursor.close()
        if row is None:
            raise HTTPException(status_code=400, detail="User not found")

        user = {
            "username": row[0],
            "password": row[1],
            "birthday": row[2],
            "last_login": row[3],
            "create_time": row[4],
            "nickName": row[5]
        }
        return {"user":user}
    else:
       raise HTTPException(status_code=401, detail="Unauthorized")

@app.post("/user/")
def create_user(user: User, db: connection = Depends(get_db)):
        query = 'SELECT COUNT(*) FROM public."users" WHERE "username" = %s'
        insert_query = 'INSERT INTO public."users" ("username", "password", "create_time", "birthday") VALUES (%s, %s, %s, %s)'
        cursor = db.cursor()

        cursor.execute(query, (user.username,))
        count = cursor.fetchone()[0]
        if count > 0:
            cursor.close()
            raise HTTPException(status_code=400, detail="User already exists")
        
        password_hash = sha256(user.password.encode('utf-8')).hexdigest()
        cursor.execute(insert_query, (user.username, password_hash, user.create_time, user.birthday))
        db.commit()
        cursor.close()
        return {"message": "User created"}
    # else:
    #    raise HTTPException(status_code=401, detail="Unauthorized")

@app.delete("/user/")
def delete_user(username: str = Form(...), Authorization:str = Header(...), db: connection = Depends(get_db)):
    result = verify_identity(Authorization, db)
    if result[0]:
        if(result[1] != 'admin'):#verify
            raise HTTPException(status_code=401, detail="Not admin")
        if(username == 'admin'):#prevent from deleting admin
            raise HTTPException(status_code=403, detail="Admin cannot be deleted")
        query = 'SELECT COUNT(*) FROM public."users" WHERE "username" = %s'
        delete_query = 'DELETE FROM public."users" WHERE "username" = %s'

        cursor = db.cursor()
        cursor.execute(query, (username,))
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.close()
            raise HTTPException(status_code=400, detail="User does not exist")

        cursor.execute(delete_query, (username,))
        db.commit()
        cursor.close()
        return {"message": "User deleted"}
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.patch("/user/")
def update_user(user:User, Authorization:str = Header(...), db: connection = Depends(get_db)):
    result = verify_identity(Authorization, db)
    if result[0]:
        # check if empty
        user.username = result[1]
        if not user.username or not user.password:
            raise HTTPException(status_code=400, detail="Invalid update data")
        query = 'SELECT COUNT(*) FROM public."users" WHERE "username" = %s'
        update_query = 'UPDATE public."users" SET "password" = %s, "birthday" = %s WHERE "username" = %s'

        cursor = db.cursor()

        cursor.execute(query, (user.username,))
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.close()
            raise HTTPException(status_code=400, detail="User does not exist")

        password_hash = sha256(user.password.encode('utf-8')).hexdigest()
        cursor.execute(update_query, (password_hash, user.birthday, user.username))
        db.commit()
        cursor.close()
        return {"message": "User updated"}


@app.get("/")
def get_all_users(Authorization:str = Header(...), db: connection = Depends(get_db)):
    result = verify_identity(Authorization, db)
    if result[0]:
        username = result[1]
        if(username != 'admin'):
            raise HTTPException(status_code=401, detail="Unauthorized")
        query = 'SELECT * FROM public."users" WHERE "username" <> \'admin\' ORDER BY "username" ASC '
        cursor = db.cursor()
        cursor.execute(query)
        users = []
        rows = cursor.fetchall()
        for row in rows:
            user = {
                "name": row[0],
                "password": row[1],
                "birthday": row[2],
                "last_login": row[3],
                "create_time": row[4],
            }
            users.append(user)
        cursor.close()
        return {"users": users}
    
# @app.post("/upload-video/")
# async def upload_video(video_data: Video, username: str = Header(...), db: connection = Depends(get_db)):
#     # Save video file to server
#     with open(f"videos/{video_data.title}.mp4", "wb") as f:
#         f.write(video_data.video_data)

#     # Create video record in database
#     insert_query = 'INSERT INTO videos (title, description, filename) VALUES (%s, %s, %s) RETURNING video_id'
#     cursor = db.cursor()
#     cursor.execute(insert_query, (video_data.title, video_data.description, f"{video_data.title}.mp4"))
#     video_id = cursor.fetchone()[0]
#     db.commit()

#     # Associate uploaded video with user
#     insert_user_video_query = 'INSERT INTO user_videos (username, video_id) VALUES (%s, %s)'
#     cursor.execute(insert_user_video_query, (username, video_id))
#     db.commit()

#     cursor.close()

#     return {"message": "Video uploaded successfully"}
