from fastapi import APIRouter,HTTPException,Query
from fastapi.responses import JSONResponse
from DBSchema_Handler import DBSchema_Handler
from sqlalchemy import Table,MetaData,select,func,insert,delete
from sqlalchemy.engine import Result
from pydantic import BaseModel,EmailStr
from datetime import datetime
import json
from helper.configurationandloggerhandler import ConfigurationAndLoggerHandler

"""Initiate logger"""

config_and_logger=ConfigurationAndLoggerHandler()
config=config_and_logger.read_configuration('api.configuration')
logger=config_and_logger.setup_logger('api-userManagement',config['logsdirectory'])


"""Initiate API router"""
router = APIRouter(prefix='/users')

"""Database Connections Setup"""
dbcomp=DBSchema_Handler()
metadata_obj = MetaData()
engine=dbcomp.create_alchemy_engine()
users_authority = Table("users_authority", metadata_obj, autoload_with=engine)

class user_template(BaseModel):
    username: str
    email: EmailStr
    password: str
    group: int=1

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
            stmt = insert(users_authority).values(user_id=max_id+1 if max_id else 1, username=item.username,email=item.email,password=item.password,group_id=1,creation_date=datetime.now())
            conn.execute(stmt)
            conn.commit()
            logger.info('User Created:{item.username}')
            return JSONResponse(status_code=200,content={"result":"User Created"})

@router.delete('/userdelete')
async def delete_user(username:str=Query(...,min_length=3)):
    if does_user_exist(username):
        with engine.connect() as conn:
            stmt = delete(users_authority).where(username==username)
            conn.execute(stmt)
            conn.commit()
            logger.info('User Deleted:{username}')
            return JSONResponse(status_code=200,content={"result":"User Deleted"})
    else:
        raise HTTPException(status_code=404,detail='User not exist')