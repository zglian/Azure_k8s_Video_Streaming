from fastapi import HTTPException
from jose import jwt
from datetime import datetime, date, timedelta
from . import config
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer

DATABASE_URL = config.DATABASE_URL
SECRET_KEY = config.SECRET_KEY 
ALGORITHM = config.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES= config.ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_jwt_token(username: str) -> str:
    expiration = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"username": username, "exp": expiration}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_jwt_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
    except:
        raise HTTPException(status_code=401, detail="Invalid token signature")
    
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

