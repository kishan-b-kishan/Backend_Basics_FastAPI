from fastapi import status,HTTPException , Depends, APIRouter
from sqlalchemy.orm import Session
from database import get_db
import tables
from passlib.context import CryptContext
from routers import jwts
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
router = APIRouter(tags=['Authentication'])



pwd_context= CryptContext(schemes=["bcrypt"], deprecated="auto")
                          
@router.post('/login')
def login(usercred: OAuth2PasswordRequestForm = Depends(),db: Session = Depends(get_db)): #We use OAuth2PasswordRequestForm here because,
    #it is a standard way of sending username and password in the body of the request. It is a form data and not a json data. 
    # So we use OAuth2PasswordRequestForm to get the username and password from the form data.
    user= db.query(tables.User).filter(tables.User.email == usercred.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid credentials")
    #cur_hashed_password = pwd_context.hash(usercred.password)
    #actual_hashed_password = user.password
    #The above method doesnt work with .verify() 
    #because hashing the newly entered password even tho would be correct would be hashed using a new salt by CrytContext so it wont match,
    #.verify()takes the fresh password and comapres with the salt of the hashed password and then uses the same format to hash and verify
    if not pwd_context.verify(usercred.password,user.password): #first para is postman req, second para is db hashed password
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid credentials")
    
    access_token= jwts.create_access_token(data = {"user_id":user.id})
    return {"token": access_token , "token_type":"bearer"}