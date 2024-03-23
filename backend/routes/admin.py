from fastapi import APIRouter, HTTPException, Header, Form, Depends
from sqlalchemy.orm import Session
from .models import *
from .database import get_db
from .users import verify_jwt_token, verify_identity
from .config import *

router = APIRouter()

@router.delete("/user/")
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

@router.get("/")
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