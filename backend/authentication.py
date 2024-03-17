from fastapi import HTTPException
from jose import jwt
from datetime import datetime, date, timedelta
import config
import psycopg2

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
    
def verify_user_from_db(username: str, db: psycopg2.extensions.connection):
    query = 'SELECT "UserName", "password" FROM public."user" WHERE "UserName" = %s'
    cursor = db.cursor()
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    cursor.close()
    if result:
        username, password = result
        return password
    return None
