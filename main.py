from pydantic import BaseModel
import uvicorn
from fastapi import FastAPI,HTTPException,Request
from CleanWiktionaryRawLXML import CleanWiktionaryRawLXML
from API_Routers.APIs_UserManagement import router as router_usermanager
from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from typing_extensions import Annotated

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
    "Pelagia": {
        "username": "Pelagia",
        "full_name": "Pelagia Fady Zaki",
        "email": "Pelagia@gmail.com",
        "hashed_password": "HashedPasswordJesusmylord@77",
        "disabled": True,
    },
}

class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str

"""Create FaseApi Object"""
app=FastAPI(title="Word Interogation")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app.include_router(router_usermanager)

@app.get("/")
def read_root():
    return "Server is running."

@app.get("/items/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}

@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    print(f"--------->{form_data.username}")
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    print(user_dict)
    user = UserInDB(**user_dict)
    hashed_password = "HashedPassword"+form_data.password
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    print({"access_token": user.username, "token_type": "bearer"})
    return {"access_token": user.username, "token_type": "bearer"}


def main()->None:
    """Clean Wiktionary data"""
    ...

if __name__=='__main__':
    main()
    uvicorn.run("main:app",host="0.0.0.0", port=8000, reload=False, log_level="debug",workers=1)
