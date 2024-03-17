from sqlalchemy import Column, Integer, String, Date, UnicodeText, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    UserName = Column(String, primary_key = True)
    password = Column(String, nullable = False)
    birthday = Column(Date)
    last_login = Column(DateTime)
    create_time = Column(DateTime)