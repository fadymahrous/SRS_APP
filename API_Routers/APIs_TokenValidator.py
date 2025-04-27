from typing import Annotated
from sqlalchemy import Table,select
import jwt
from helper.DBSchema_Handler import DBSchema_Handler
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY="n'L!T:e]lN/C'q1w5#3y[C7u6+X"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

"""FastAPI"""
router = APIRouter(prefix='/loginsection')

"""Create Database Connections using SqlAlchemy"""
database_engine_and_metadate=DBSchema_Handler()
engine,metadata=database_engine_and_metadate.create_alchemy_engine()
users_authority=Table("users_authority",metadata,autoload_with=engine)

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    username: str
    group_id: int

def get_user(username: str):
    with engine.connect() as conn:
        user_dict=conn.execute(select(users_authority).where(users_authority.c.username==username)).fetchone()
        if user_dict:
            return User(**user_dict._mapping)
    return None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
async def validate_user_token(token: Annotated[str, Depends(oauth2_scheme)]):
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

