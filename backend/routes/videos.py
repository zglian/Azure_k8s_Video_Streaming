from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .models import *
from .database import get_db

router = APIRouter()

@router.get("/videos/")
async def get_all_video_titles(db: Session = Depends(get_db)):
    videos_from_db  = db.query(Video).all()
    videos = []
    for video in videos_from_db:
        video_data = {"title": video.title, "url": video.url}
        video_data["preview_url"] = video.url.replace(".mp4", ".jpg")
        videos.append(video_data)
    db.close()
    return {"videos": videos}