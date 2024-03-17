import psycopg2
from fastapi import FastAPI, HTTPException, Header, Form, Depends 
from datetime import datetime, date, timedelta
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import config
from hashlib import sha256

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
    birthday:date = None
    last_login:datetime = None
    create_time:datetime = datetime.utcnow()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

'''
# def connect_to_db():
#     return psycopg2.connect(DATABASE_URL)

# def get_db():
#     db = connect_to_db()
#     try:
#         yield db
#     finally:
#         db.close()

# @app.on_event("startup")
# def startup():
#     app.db_connection = connect_to_db()

# @app.on_event("shutdown")
# def shutdown():
#     app.db_connection.close()


# def verify_user_from_db(username: str, db: psycopg2.extensions.connection):
#     query = 'SELECT "UserName", "password" FROM public."user" WHERE "UserName" = %s'
#     cursor = db.cursor()
#     cursor.execute(query, (username,))
#     result = cursor.fetchone()
#     cursor.close()
#     if result:
#         username, password = result
#         return password
#     return None

# def create_jwt_token(username: str) -> str:
#     expiration = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     payload = {"username": username, "exp": expiration}
#     return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# def verify_jwt_token(token: str) -> dict:
#     try:
#         return jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
#     except:
#         raise HTTPException(status_code=401, detail="Invalid token signature")

'''

def update_last_login(username: str, last_login: datetime, db: psycopg2.extensions.connection):
    update_query = 'UPDATE public."user" SET "last_login" = %s WHERE "UserName" = %s'
    cursor = db.cursor()
    cursor.execute(update_query, (last_login, username))
    db.commit()
    cursor.close()
    return {"message": "last_login updated"}

def verify_identity(token: str = Header(..., convert_underscores=True), db: psycopg2.extensions.connection = Depends(get_db)):
    payload = verify_jwt_token(token)
    username = payload["username"]
    stored_password = verify_user_from_db(username, db)
    if stored_password is None:
         raise HTTPException(status_code=401, detail="User not found")
    return (True,username)

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...), db: psycopg2.extensions.connection = Depends(get_db)):
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
def get_username(Authorization:str = Header(...), db: psycopg2.extensions.connection = Depends(get_db)):
    result = verify_identity(Authorization, db)
    if result[0]:
        username = result[1]
        query = 'SELECT * FROM public."user" WHERE "UserName" = %s'
        # conn = app.db_connection
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
def create_user(user: User, db: psycopg2.extensions.connection = Depends(get_db)):#, Authorization:str = Header(...)):
    # if verify_identity(Authorization):
        query = 'SELECT COUNT(*) FROM public."user" WHERE "UserName" = %s'
        insert_query = 'INSERT INTO public."user" ("UserName", "password", "create_time", "birthday") VALUES (%s, %s, %s, %s)'

        # conn = app.db_connection
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
def delete_user(username: str = Form(...), Authorization:str = Header(...), db: psycopg2.extensions.connection = Depends(get_db)):
#def delete_user(Authorization:str = Header(...)):
    result = verify_identity(Authorization, db)
    if result[0]:
        if(result[1] != 'admin'):#verify
            raise HTTPException(status_code=401, detail="Not admin")
        if(username == 'admin'):#prevent from deleting admin
            raise HTTPException(status_code=403, detail="Admin cannot be deleted")
        query = 'SELECT COUNT(*) FROM public."user" WHERE "UserName" = %s'
        delete_query = 'DELETE FROM public."user" WHERE "UserName" = %s'
        # conn = app.db_connection
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
def update_user(user:User, Authorization:str = Header(...), db: psycopg2.extensions.connection = Depends(get_db)):
    result = verify_identity(Authorization, db)
    if result[0]:
        # check if empty
        user.username = result[1]
        if not user.username or not user.password:
            raise HTTPException(status_code=400, detail="Invalid update data")
        query = 'SELECT COUNT(*) FROM public."user" WHERE "UserName" = %s'
        update_query = 'UPDATE public."user" SET "password" = %s, "birthday" = %s WHERE "UserName" = %s'

        # conn = app.db_connection
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
def get_all_users(Authorization:str = Header(...), db: psycopg2.extensions.connection = Depends(get_db)):
    result = verify_identity(Authorization, db)
    if result[0]:
        username = result[1]
        if(username != 'admin'):
            raise HTTPException(status_code=401, detail="Unauthorized")
        query = 'SELECT * FROM public."user" WHERE "UserName" <> \'admin\' ORDER BY "UserName" ASC '
        # conn = app.db_connection
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