from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, UnicodeText, DateTime, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    username = Column(String, primary_key = True)
    password = Column(String, nullable = False)
    email = Column(String(100), unique=True, nullable=False)
    birthday = Column(Date)
    last_login = Column(DateTime)
    create_time = Column(DateTime)

class Video(Base):
    __tablename__ = 'videos'

    video_id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    # url = Column(String(255), nullable=False)
    video_data = Column(LargeBinary)

class UserVideo(Base):
    __tablename__ = 'user_videos'

    username = Column(String, ForeignKey('users.username'), primary_key=True)
    video_id = Column(Integer, ForeignKey('videos.video_id'), primary_key=True)

    user = relationship("User", backref="user_videos")
    video = relationship("Video", backref="user_videos")
