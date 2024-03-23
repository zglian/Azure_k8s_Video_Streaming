from fastapi import APIRouter, HTTPException, Header, Form, Depends
from hashlib import sha256
from sqlalchemy.orm import Session
from .models import *
import pytz
from .config import *
from .authentication import create_jwt_token, verify_jwt_token
from .database import get_db

router = APIRouter()


@router.post("/login")
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

@router.get("/user/")
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

@router.post("/user/")
def create_user(user : UserModel, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    password_hash = sha256(user.password.encode('utf-8')).hexdigest()
    new_user = User(username=user.username, password=password_hash, email = user.email, create_time=datetime.utcnow(), birthday=user.birthday)
    db.add(new_user)
    db.commit()
    return {"message": "User created"}

@router.patch("/user/")
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

@router.post("/verify")
def verify_identity(token: str = Header(..., convert_underscores=True), db: Session= Depends(get_db)):
    payload = verify_jwt_token(token)
    username = payload["username"]
    user = db.query(User).filter(User.username == username).first()
    return user