from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, UnicodeText, DateTime, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, date
from pydantic import BaseModel
from fastapi import UploadFile

Base = declarative_base()

class UserModel(BaseModel):
    username: str
    password: str
    email: str
    birthday: date

class VideoModel(BaseModel):
    video_id: int
    title: str
    description: str 

class User(Base):
    __tablename__ = 'users'

    username = Column(String, primary_key = True)
    password = Column(String, nullable = False)
    email = Column(String(100), unique=True, nullable=False)
    birthday = Column(Date)
    last_login = Column(DateTime(timezone=True))
    create_time = Column(DateTime(timezone=True), default=datetime.utcnow)

class Video(Base):
    __tablename__ = 'videos'

    video_id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    video_data = Column(LargeBinary)

class UserVideo(Base):
    __tablename__ = 'user_videos'

    username = Column(String, ForeignKey('users.username'), primary_key=True,)
    video_id = Column(Integer, ForeignKey('videos.video_id'), primary_key=True)
    watched_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    user = relationship("User", backref="user_videos")
    video = relationship("Video", backref="user_videos")
