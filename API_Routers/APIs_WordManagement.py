from fastapi import APIRouter,HTTPException,Depends
from fastapi.responses import JSONResponse
from sqlalchemy import Table,and_,select,func,insert,delete,bindparam,update
from datetime import datetime,timedelta
from helper.configurationandloggerhandler import ConfigurationAndLoggerHandler
from helper.DBSchema_Handler import DBSchema_Handler
from API_Routers.APIs_TokenValidator import validate_user_token
from Sm2_Review_Equation import Sm2_Review_Equation

"""Initiate logger"""
config_and_logger=ConfigurationAndLoggerHandler()
config=config_and_logger.read_configuration('api.configuration')
logger=config_and_logger.setup_logger('api-wordManagement',config['logsdirectory'])

"""Database Connections Setup"""
dbcomp=DBSchema_Handler()
engine,metadata_obj=dbcomp.create_alchemy_engine()
users_words = Table("user_words", metadata_obj, autoload_with=engine)
users_authority = Table("users_authority", metadata_obj, autoload_with=engine)

"""Create Object of the SM Equation"""
sm2_rating=Sm2_Review_Equation()


"""Initiate API router"""
router = APIRouter(prefix='/word')

@router.post('/addword')
def add_word(word:str,user=Depends(validate_user_token)):
    """Check if Word already exist in User pool"""
    stmt=select(users_words.c.word).join(users_authority).where(and_(users_authority.c.username == user.username,users_words.c.word == word))
    with engine.connect() as conn:
        word_already_exist=conn.execute(stmt).fetchone()
        if word_already_exist:
            return JSONResponse(status_code=409, content={"Result": "Word already exist"})
    """Insert the Word"""
    stmt=insert(users_words).values(user_id=select(users_authority.c.user_id).where(users_authority.c.username==user.username).scalar_subquery(),word=word,exercise_date=datetime.now(),quality=0,efficiency=0,interval=0,repetition=0)
    print(stmt)
    try:
        with engine.connect() as conn:
            word_already_exist=conn.execute(stmt)
            conn.commit()
    except Exception as e:
        logger.exception(f'Word can not be added for the following exception {e}')
        raise HTTPException(status_code=404, detail="Cant Add the word,Exception raised")
    return JSONResponse(status_code=200, content={"Result": "Word Added successfully"})

@router.get('/todaywordslist')
def get_word_list(user=Depends(validate_user_token)):
    stmt=select(users_words.c.word).join(users_authority).where(and_(users_authority.c.username==user.username,users_words.c.exercise_date < datetime.now()))
    try:
        with engine.connect() as conn:
            result=conn.execute(stmt)
            words_list = result.scalars().all()
            number_of_words=len(words_list)
    except Exception as e:
        logger.exception(f'Failed to fetch word list due to: {e}')
        raise e
    return JSONResponse(status_code=200, content={"Result": words_list,"count":number_of_words})

@router.get('/parcticenextword')
def get_word_list(user=Depends(validate_user_token)):
    stmt=select(users_words.c.word).join(users_authority).where(and_(users_authority.c.username==user.username,users_words.c.exercise_date < datetime.now())).order_by(users_words.c.exercise_date)
    try:
        with engine.connect() as conn:
            result=dict(conn.execute(stmt).fetchone()._mapping.items())
            result['exercise_date']=result['exercise_date'].isoformat()
    except Exception as e:
        logger.exception(f'Failed to fetch word next word due to: {e}')
        raise e
    return JSONResponse(status_code=200, content={"Result": result})

@router.post('/rateword')
def add_word(word:str,quality:int,user=Depends(validate_user_token)):
    """Check if Word already exist in User pool"""
    stmt=select(users_words).join(users_authority).where(and_(users_authority.c.username == user.username,users_words.c.word == word))
    with engine.connect() as conn:
        word_parameters=conn.execute(stmt).fetchone()
        word_parameters_dict=dict(word_parameters._mapping.items()) 
        word_parameters_dict['quality']=quality
    """New Rating Making"""
    sm2_review_output=sm2_rating.sm2_review(word_parameters_dict)
    stmt=update(users_words).where(and_(users_authority.c.username == user.username,users_words.c.word == word)).values(exercise_date=sm2_review_output.exercise_date,quality=sm2_review_output.quality,efficiency=sm2_review_output.efficiency,interval=sm2_review_output.interval,repetition=sm2_review_output.repetition)
    try:
        with engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()
    except Exception as e:
        logger.exception(f'Word rating update {e}')
        raise HTTPException(status_code=404, detail="Cant update word ratings,Exception raised")
    return JSONResponse(status_code=200, content={"Result": "Word Rated successsfully"})