from fastapi import APIRouter,HTTPException,Depends
from fastapi.responses import JSONResponse
from sqlalchemy import Table,and_,select,func,insert,delete,bindparam
from sqlalchemy.engine import Result
from pydantic import BaseModel,EmailStr
from datetime import datetime
from helper.configurationandloggerhandler import ConfigurationAndLoggerHandler
from helper.DBSchema_Handler import DBSchema_Handler
from API_Routers.APIs_TokenValidator import validate_user_token

"""Initiate logger"""
config_and_logger=ConfigurationAndLoggerHandler()
config=config_and_logger.read_configuration('api.configuration')
logger=config_and_logger.setup_logger('api-wordManagement',config['logsdirectory'])

"""Database Connections Setup"""
dbcomp=DBSchema_Handler()
engine,metadata_obj=dbcomp.create_alchemy_engine()
users_words = Table("user_words", metadata_obj, autoload_with=engine)
users_authority = Table("users_authority", metadata_obj, autoload_with=engine)

"""Initiate API router"""
router = APIRouter(prefix='/word')

@router.post('/addword')
def add_word(word:str,user=Depends(validate_user_token)):
    scaler_userid = (select(users_authority.c.user_id).where(and_(users_words.c.user_id == scaler_userid, users_words.c.word == word)
).scalar_subquery())
    stmt=select(users_words).where(users_words.c.user_id==scaler_userid and users_words.c.word==word)
    with engine.connect() as conn:
        word_already_exist=conn.execute(stmt)
    if word_already_exist:
        return JSONResponse(status_code=409, content={"Result": "Word already exist"})
    stmt=insert(users_words).values(user_id=scaler_userid,word_id=word,last_seen=datetime.now(),raised_to_user=1,quality=0)
    try:
        with engine.begin() as conn:
            conn.execute(stmt)
    except Exception as e:
        logger.exception(f'Word can not be added for the following exception {e}')
        raise HTTPException(status_code=404, detail="Cant Add the word,Exception raised")
    return JSONResponse(status_code=200, content={"Result": "Word Added successfully"})

@router.get('/wordslist')
def get_word_list(user=Depends(validate_user_token)):
    scaler_userid = (select(users_authority.c.user_id).where(users_authority.c.username == user.username).scalar_subquery())
    stmt=select(users_words.c.word_id).where(users_words.c.user_id==scaler_userid)
    try:
        with engine.connect() as conn:
            result=conn.execute(stmt).scalars().all()
            words_list = list(result)
    except Exception as e:
        logger.exception(f'Failed to fetch word list due to: {e}')
        raise e
    return JSONResponse(status_code=200, content={"Result": words_list})
