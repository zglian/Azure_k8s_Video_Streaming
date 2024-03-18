from fastapi import FastAPI, HTTPException, Header, Form, Depends, UploadFile, File
from datetime import datetime, date
from fastapi.middleware.cors import CORSMiddleware
import config
from hashlib import sha256
from sqlalchemy.orm import Session
import os
from psycopg2.extensions import connection
from models import *
import pytz
from pathlib import Path
import uuid

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
def delete_user(username: str = Form(...), Authorization:str = Header(...), db: Session = Depends(get_db)):
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

@app.post("/upload-video/")
async def upload_video(video_upload: VideoModel, video_data: UploadFile = File(...), db: Session = Depends(get_db)):
    title = video_upload.title
    description = video_upload.description
    # title = "video1"
    # description = "video_upload.description"
    
    # with open(f"../video_dataset/{video_data.filename}", "wb") as f:
    #     f.write(video_data.file.read())

    video_file_path = '../video_dataset/video-1.mp4'  # 更新為影片檔案的正確路徑
    with open(video_file_path, 'rb') as f:
        video_data = f.read()

    # video_id = uuid.uuid4()

    new_video = Video(title=title, description=description, video_data=video_data)
    db.add(new_video)
    db.commit()

    # # 關聯上傳的視頻與用戶
    # new_video.usernames.append(username)
    db.commit()
    return {"message": "Video uploaded successfully"}

@app.post("/watch-video/{video_id}/")
def watch_video(video_id: int, Authorization: str = Header(...), db: Session = Depends(get_db)):
    user = verify_identity(Authorization, db)
    
    video = db.query(Video).filter(Video.video_id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # 標記該用戶觀看了這個影片
    user_video = db.query(UserVideo).filter(UserVideo.username == user.username, UserVideo.video_id == video_id).first()
    if user_video:
        user_video.watched_at = datetime.utcnow()
    else:
        user_video = UserVideo(username=user.username, video_id=video_id, watched_at=datetime.utcnow())
        db.add(user_video)
    
    db.commit()
    return {"message": "Video watched successfully"}