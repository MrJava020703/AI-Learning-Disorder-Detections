from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from .core import settings
from .database import get_db
from .models import User
pwd=CryptContext(schemes=['bcrypt'],deprecated='auto')
oauth2=OAuth2PasswordBearer(tokenUrl='/api/auth/login')
def hash_password(password): return pwd.hash(password)
def verify_password(password, hashed): return pwd.verify(password,hashed)
def create_token(user): return jwt.encode({'sub':str(user.id),'role':user.role,'exp':datetime.now(timezone.utc)+timedelta(hours=12)},settings.jwt_secret,algorithm='HS256')
def current_user(token:str=Depends(oauth2),db:Session=Depends(get_db)):
    try: uid=int(jwt.decode(token,settings.jwt_secret,algorithms=['HS256'])['sub'])
    except (JWTError,KeyError,ValueError): raise HTTPException(401,'Invalid or expired session')
    user=db.get(User,uid)
    if not user: raise HTTPException(401,'Account not found')
    return user
