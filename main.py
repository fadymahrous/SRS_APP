from pydantic import BaseModel
import uvicorn
from fastapi import FastAPI,HTTPException,Request
from CleanWiktionaryRawLXML import CleanWiktionaryRawLXML
from API_Routers.APIs_UserManagement import router as router_usermanager
from API_Routers.APIs_SecureLogin import router as router_securelogin
from API_Routers.APIs_WordManagement import router as router_wordmanagment
from fastapi import Depends, FastAPI
from helper.DBSchema_Handler import DBSchema_Handler

class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None

class UserInDB(User):
    hashed_password: str

""" Create missing tables"""
db_handle=DBSchema_Handler()
db_handle.createschema()

"""Create FaseApi Object"""
app=FastAPI(title="Word Interogation")
app.include_router(router_usermanager)
app.include_router(router_securelogin)
app.include_router(router_wordmanagment)


@app.get("/")
def read_root():
    return "Server is running."

def main()->None:
    """Clean Wiktionary data,For time Being i will do it manually"""
    """Create databse schema and add any msissing table"""
    ...

if __name__=='__main__':
    main()
    uvicorn.run("main:app",host="0.0.0.0", port=8000, reload=False, log_level="debug",workers=1)
