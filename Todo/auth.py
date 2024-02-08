from typing import Optional
from fastapi import FastAPI, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from database import engine, SessionLocal
from pydantic import BaseModel
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import models

SECRET_KEY = '197b2c37c391bed93fe80344fe73b806947a65e36aa6e05a1a23c2fa12702fe3'
ALGORITHM = 'HS256'


class UserRequest(BaseModel):
    username: str
    password: str
    email: Optional[str]
    first_name: str
    last_name: str


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
models.Base.metadata.create_all(bind=engine)
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="login")
app = FastAPI()


def get_hashed_password(password: str) -> str:
    return bcrypt_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str, db):
    user = db.query(models.Users).filter(models.Users.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


async def get_current_user(token: str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: str = payload.get("id")

        if user_id is None or username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')
        return {"username": username, "id": user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')


def get_access_token(username: str, user_id: int, expires_delta: Optional[timedelta] = None):
    encode = {"sub": username, "id": user_id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


@app.post("/create/user")
async def create_user(user: UserRequest, db: Session = Depends(get_db)):
    new_model_user = models.Users()
    new_model_user.username = user.username
    new_model_user.password = get_hashed_password(user.password)
    new_model_user.email = user.email
    new_model_user.first_name = user.first_name
    new_model_user.last_name = user.last_name
    new_model_user.is_active = True

    db.add(new_model_user)
    db.commit()

    return new_model_user


@app.post("/login")
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')

    token_expire = timedelta(minutes=20)
    token = get_access_token(username=user.username, user_id=user.id, expires_delta=token_expire)
    return {"token": token}
