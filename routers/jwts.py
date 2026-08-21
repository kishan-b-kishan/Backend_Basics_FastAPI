from jose import JWTError, jwt
from datetime import datetime,timedelta
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
import os
from fastapi import FastAPI,status,HTTPException , Depends 
from fastapi.security import OAuth2PasswordBearer

load_dotenv()
SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 90

class Token(BaseModel):
    token :str
    token_type : str

class TokenData(BaseModel):
    id: int

def create_access_token(data:dict):
    to_encode = data.copy()

    expire = datetime.utcnow()+timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    jwt_token  = jwt.encode(to_encode, SECRET_KEY , algorithm = ALGORITHM)

    return jwt_token

def verify_access_token(token: str,credexcep):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])

        id :str = payload.get("user_id")
        if not id:
            raise credexcep
        token_data=TokenData(id =id)
    except JWTError:
        raise credexcep
    return token_data
    
def get_cur_user(token : str = Depends(OAuth2PasswordBearer(tokenUrl='login'))):
    credexcep = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials", headers={"WWW-Authenticate":"Bearer"})
    return verify_access_token(token,credexcep)