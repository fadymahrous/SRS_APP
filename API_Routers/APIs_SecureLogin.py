from datetime import datetime, timedelta, timezone
from typing import Annotated
from sqlalchemy import Table,select
import jwt
from helper.DBSchema_Handler import DBSchema_Handler
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.hash import pbkdf2_sha256
from pydantic import BaseModel

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY="n'L!T:e]lN/C'q1w5#3y[C7u6+X"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

"""FastAPI"""
router = APIRouter(prefix='/auth')

"""Create Database Connections using SqlAlchemy"""
database_engine_and_metadate=DBSchema_Handler()
engine,metadata=database_engine_and_metadate.create_alchemy_engine()
users_authority=Table("users_authority",metadata,autoload_with=engine)


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    username: str
    email: str | None = None

class UserInDB(User):
    password: str

def verify_password(plain_password, hashed_password):
    result=pbkdf2_sha256.verify(SECRET_KEY+plain_password, hashed_password)
    return result

def get_user(username: str):
    with engine.connect() as conn:
        user_dict=conn.execute(select(users_authority).where(users_authority.c.username==username)).fetchone()
        if user_dict:
            return UserInDB(**user_dict._mapping)
    return None

def authenticate_user(username: str, password: str):
    user_dict = get_user(username)
    if not user_dict:
        return False
    if not verify_password(password,user_dict.password):
        return False
    return user_dict

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    '''
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    '''
    return current_user


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@router.get("/me/")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user
