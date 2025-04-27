from pydantic import BaseModel
import uvicorn
from fastapi import FastAPI,HTTPException,Request
from CleanWiktionaryRawLXML import CleanWiktionaryRawLXML
from API_Routers.APIs_UserManagement import router as router_usermanager
from API_Routers.APIs_SecureLogin import router as router_securelogin
from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from typing_extensions import Annotated

class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str

"""Create FaseApi Object"""
app=FastAPI(title="Word Interogation")
app.include_router(router_usermanager)
app.include_router(router_securelogin)


@app.get("/")
def read_root():
    return "Server is running."

def main()->None:
    """Clean Wiktionary data"""
    ...

if __name__=='__main__':
    main()
    uvicorn.run("main:app",host="0.0.0.0", port=8000, reload=False, log_level="debug",workers=1)
