from fastapi import FastAPI, HTTPException, Header, Form, Depends, UploadFile, File, Response
from starlette.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import config
from hashlib import sha256
from sqlalchemy.orm import Session
from models import *
import pytz
from pathlib import Path
import os
import cv2


from authentication import create_jwt_token, verify_jwt_token
from database import get_db


CHUNK_SIZE = 1024*1024
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
    # if not user.username or not user.password:
    #     raise HTTPException(status_code=400, detail="Invalid update data: Password is required")
    result = verify_identity(Authorization, db)
    # if user.username != result.username:
    #     raise HTTPException(status_code=403, detail="Forbidden: User can only update their own information")
    
    existing_user = db.query(User).filter(User.username == result.username).first()
    if existing_user is None:
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

# @app.post("/watch-video/{video_id}/")
# def watch_video(video_id: int, Authorization: str = Header(...), db: Session = Depends(get_db)):
#     user = verify_identity(Authorization, db)
    
#     video = db.query(Video).filter(Video.video_id == video_id).first()
#     if not video:
#         raise HTTPException(status_code=404, detail="Video not found")

#     # 標記該用戶觀看了這個影片
#     user_video = db.query(UserVideo).filter(UserVideo.username == user.username, UserVideo.video_id == video_id).first()
#     if user_video:
#         user_video.watched_at = datetime.utcnow()
#     else:
#         user_video = UserVideo(username=user.username, video_id=video_id, watched_at=datetime.utcnow())
#         db.add(user_video)
    
#     db.commit()
#     return {"message": "Video watched successfully"}

# video_path = Path("video-1.mp4")


@app.get("/video/{video_name}")
async def video_endpoint(video_name: str):
    video_path = Path(f"./videos/{video_name}")
    return FileResponse(video_path, media_type="video/mp4")

'''@app.get("/video/{video_name}")
async def video_endpoint(video_name: str, range: str = Header(None)):
    start, end = range.replace("bytes=", "").split("-")
    start = int(start)
    end = int(end) if end else start + CHUNK_SIZE
    video_path = Path(video_name)
    # video_path = Path("video-1.mp4")
    with open(video_path, "rb") as video:
        video.seek(start)
        data = video.read(end - start)
        filesize = str(video_path.stat().st_size)
        headers = {
            'Content-Range': f'bytes {str(start)}-{str(end)}/{filesize}',
            'Accept-Ranges': 'bytes'
        }
        return Response(data, status_code=206, headers=headers, media_type="video/mp4")
'''


@app.get("/previews/{preview_url}")
async def video_endpoint(preview_url: str):
    iamge_path = Path(f"./previews/{preview_url}")
    return FileResponse(iamge_path, media_type="image/jpg")

@app.get("/videos/")
async def get_all_video_titles(db: Session = Depends(get_db)):
    videos_from_db  = db.query(Video).all()
    videos = []
    for video in videos_from_db:
        video_data = {"title": video.title, "url": video.url}
        preview_image_path = f"./previews/{video.title}.jpg"
        video_path = f"./videos/{video.url}"
        generate_preview_image(video_path, preview_image_path)
        video_data["preview_url"] = video.title + ".jpg"
        videos.append(video_data)
    db.close()
    return {"videos": videos}

def generate_preview_image(video_path: str, preview_image_path: str):
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    cv2.imwrite(preview_image_path, frame)
    cap.release

@app.post("/upload/")
async def upload_video(video: UploadFile = File(...)):
    contents = await video.read()
    # 將 contents 寫入到您的存儲位置，這裡示例中直接返回內容
     # 指定存儲路徑
    upload_folder = "upload_videos"
    # 確保上傳文件夾存在
    os.makedirs(upload_folder, exist_ok=True)
    # 寫入文件
    file_path = os.path.join(upload_folder, video.filename)
    with open(file_path, "wb") as f:
        f.write(contents)
    return file_path