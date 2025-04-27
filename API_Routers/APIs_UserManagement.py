from fastapi import APIRouter,HTTPException,Query,Depends
from fastapi.responses import JSONResponse
from helper.DBSchema_Handler import DBSchema_Handler
from sqlalchemy import Table,select,func,insert,delete
from sqlalchemy.engine import Result
from pydantic import BaseModel,EmailStr
from datetime import datetime
from passlib.hash import pbkdf2_sha256
from helper.configurationandloggerhandler import ConfigurationAndLoggerHandler
from API_Routers.APIs_TokenValidator import validate_user_token 

"""Hasing Secret Key to be migrated as os.env"""
SECRET_KEY="n'L!T:e]lN/C'q1w5#3y[C7u6+X"

"""Initiate logger"""
config_and_logger=ConfigurationAndLoggerHandler()
config=config_and_logger.read_configuration('api.configuration')
logger=config_and_logger.setup_logger('api-userManagement',config['logsdirectory'])


"""Initiate API router"""
router = APIRouter(prefix='/users')

"""Database Connections Setup"""
dbcomp=DBSchema_Handler()
engine,metadata_obj=dbcomp.create_alchemy_engine()
users_authority = Table("users_authority", metadata_obj, autoload_with=engine)

class user_template(BaseModel):
    username: str
    email: EmailStr
    password: str
    group: int=1
    status:int=0

def hash_password(password):
    return pbkdf2_sha256.hash(SECRET_KEY+password)

def does_user_exist(username:str,mail:str=None)->bool:
    stmt_user=select(users_authority).where(users_authority.c.username==username)
    stmt_mail=select(users_authority).where(users_authority.c.username==mail)
    with engine.connect() as conn:
        result_user:Result=conn.execute(stmt_user)
        result_mail:Result=conn.execute(stmt_mail)
    if result_user.first() or result_mail.first():
        return True
    return False

@router.get("/")
async def read_users(username:str=Query(...,min_length=3)):
    stmt = select(users_authority.c.username,users_authority.c.email,users_authority.c.group_id).where(users_authority.c.username == username)
    with engine.connect() as conn:
        result: Result = conn.execute(stmt)
        user_row = result.fetchone()
    # Handle not found
    if user_row is None:
        raise HTTPException(status_code=404,detail="User not found")
    # Return as dict
    return JSONResponse(status_code=200,content={"result": dict(user_row._mapping)})

@router.post('/create')
async def create_user(item:user_template):
    if does_user_exist(item.username,item.email):
        raise HTTPException(status_code=404,detail='User already exist')
    else:
        with engine.connect() as conn:
            stmt = select(func.max(users_authority.c.user_id))
            result:Result = conn.execute(stmt)
            max_id = result.scalar()
            stmt = insert(users_authority).values(user_id=max_id+1 if max_id else 1, username=item.username,email=item.email,password=hash_password(item.password),group_id=1,creation_date=datetime.now(),status=item.status)
            conn.execute(stmt)
            conn.commit()
            logger.info(f'User Created:{item.username}')
            return JSONResponse(status_code=200,content={"result":"User Created"})

@router.delete('/userdelete')
async def delete_user(user=Depends(validate_user_token)):
    if does_user_exist(user.username):
        with engine.connect() as conn:
            stmt = delete(users_authority).where(users_authority.c.username==user.username)
            conn.execute(stmt)
            conn.commit()
            logger.info(f'User Deleted:{user.username}')
            return JSONResponse(status_code=200,content={"result":"User Deleted"})
    else:
        raise HTTPException(status_code=404,detail='User not exist')