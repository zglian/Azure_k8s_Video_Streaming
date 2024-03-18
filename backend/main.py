from fastapi import FastAPI, HTTPException, Header, Form, Depends, UploadFile, File
from datetime import datetime, date
from fastapi.middleware.cors import CORSMiddleware
import config
from hashlib import sha256
from sqlalchemy.orm import Session
import os
from psycopg2.extensions import connection
from models import User, UserModel
import pytz

from authentication import create_jwt_token, verify_jwt_token
from database import get_db

DATABASE_URL = config.DATABASE_URL
SECRET_KEY = config.SECRET_KEY 
ALGORITHM = config.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES= config.ACCESS_TOKEN_EXPIRE_MINUTES

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_identity(token: str = Header(..., convert_underscores=True), db: Session= Depends(get_db)):
    payload = verify_jwt_token(token)
    username = payload["username"]
    user = db.query(User).filter(User.username == username).first()
    return user

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    password_hash = sha256(password.encode('utf-8')).hexdigest()
    user = db.query(User).filter(User.username == username).first()
    if user is None or user.password is None or password_hash != user.password:
        raise HTTPException(status_code=401, detail="Invalid account")
    
    taipei_timezone = pytz.timezone('Asia/Taipei')
    user.last_login = datetime.now(taipei_timezone)
    db.commit()
    # 先verify user 再create token
    jwt_token = create_jwt_token(username)
    return {"username": username, "token": jwt_token}

@app.get("/user/")
def get_user_data(Authorization:str = Header(...), db: Session = Depends(get_db)):
    user = verify_identity(Authorization, db)
    if user.password:
        return {
            "user": {
                "username": user.username,
                "email": user.email,
                # "password": user.password,
                "birthday": user.birthday,
                "last_login": user.last_login,
                "create_time": user.create_time,
            }
        }
    else:
       raise HTTPException(status_code=401, detail="Unauthorized")

@app.post("/user/")
def create_user(user : UserModel, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    password_hash = sha256(user.password.encode('utf-8')).hexdigest()
    new_user = User(username=user.username, password=password_hash, email = user.email, create_time=datetime.utcnow(), birthday=user.birthday)
    db.add(new_user)
    db.commit()
    return {"message": "User created"}

@app.delete("/user/")
def delete_user(username: str = Form(...), Authorization:str = Header(...), db: connection = Depends(get_db)):
    result = verify_identity(Authorization, db)
    if(result.username != 'admin'):
        raise HTTPException(status_code=401, detail="Not admin")
    
    if(username == 'admin'):
        #prevent from deleting admin
        raise HTTPException(status_code=403, detail="Admin cannot be deleted")
    
    existing_user = db.query(User).filter(User.username == username).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(existing_user)
    db.commit()

    return {"message": "User deleted"}

@app.patch("/user/")
def update_user(user: UserModel, Authorization: str = Header(...), db: Session = Depends(get_db)):
    if not user.username or not user.password:
        raise HTTPException(status_code=400, detail="Invalid update data: Password is required")
    
    result = verify_identity(Authorization, db)
    if user.username != result.username:
        raise HTTPException(status_code=403, detail="Forbidden: User can only update their own information")
    
    existing_user = db.query(User).filter(User.username == user.username).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    existing_user.password = sha256(user.password.encode('utf-8')).hexdigest()
    existing_user.birthday = user.birthday
    existing_user.email = user.email
    db.commit()
    return {"message": "User updated"}

@app.get("/")
def get_all_users(Authorization:str = Header(...), db: Session = Depends(get_db)):
    user = verify_identity(Authorization, db)
    if(user.username != 'admin'):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    users_from_db = db.query(User).filter(User.username != 'admin').order_by(User.username.asc()).all()
    users = []
    for user in users_from_db:
        user_data = {
            "name": user.username,
            "email": user.email,
            "birthday": user.birthday,
            "last_login": user.last_login,
            "create_time": user.create_time,
        }
        users.append(user_data)

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
