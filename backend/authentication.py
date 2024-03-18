from fastapi import HTTPException
from jose import jwt
from datetime import datetime, date, timedelta
import config
# from sqlalchemy.orm import Session
# from models import User

DATABASE_URL = config.DATABASE_URL
SECRET_KEY = config.SECRET_KEY 
ALGORITHM = config.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES= config.ACCESS_TOKEN_EXPIRE_MINUTES


def create_jwt_token(username: str) -> str:
    expiration = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"username": username, "exp": expiration}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_jwt_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
    except:
        raise HTTPException(status_code=401, detail="Invalid token signature")


# def verify_user_from_db(username: str, db: Session):
#     user = db.query(User).filter(User.username == username).first()
#     if user and user.password:
#         return user.password
#     return None
