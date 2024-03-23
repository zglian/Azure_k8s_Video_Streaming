from fastapi import FastAPI, HTTPException, Header, Form, Depends, UploadFile, File, Response, Body
from starlette.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from hashlib import sha256
from sqlalchemy.orm import Session
import pytz
from pathlib import Path
import cv2
from azure.storage.blob import BlobServiceClient
import aiofiles
import os
from routes import azure, users, videos, admin

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.post("/verify")
# def verify_identity(token: str = Header(..., convert_underscores=True), db: Session= Depends(get_db)):
#     payload = verify_jwt_token(token)
#     username = payload["username"]
#     user = db.query(User).filter(User.username == username).first()
#     return user
'''@app.get("/previews/{url:path}")
async def video_endpoint(url: str):
    image_path = Path(f"./previews/{url}")
    return FileResponse(image_path, media_type="video/mp4")'''


'''@app.post("/upload/")
async def upload_video(video: UploadFile = File(...),
                       title: str = Form(),
                       description: str = Form(),
                       uploader_username: str = Form(),
                       db: Session = Depends(get_db)):
    contents = await video.read()
    upload_folder = "upload_videos"
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, video.filename)
    with open(file_path, "wb") as f:
        f.write(contents)
    new_video = Video(title=title,
                    description=description,
                    url=file_path,
                    uploader_username=uploader_username)
    db.add(new_video)
    db.commit()
    return new_video'''

'''@app.post("/upload-data/")
async def upload_video_data(video_upload: VideoModel, db: Session = Depends(get_db)):
    new_video = Video(title=video_upload.title,
                        description=video_upload.description,
                        url=video_upload.url)
    db.add(new_video)
    db.commit()

    # # 關聯上傳的視頻與用戶
    # new_video.usernames.append(username)
    # db.commit()
    return {"message": "Video uploaded successfully"}'''

'''def generate_preview_image(video_path: str, preview_image_path: str):
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    cv2.imwrite(preview_image_path, frame)
    cap.release'''

app.include_router(azure.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(videos.router)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, )    
    