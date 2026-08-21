from fastapi import status,HTTPException , Depends, APIRouter
from pydantic import BaseModel, EmailStr
from database import get_db
from sqlalchemy.orm import Session
import tables
from passlib.context import CryptContext

router = APIRouter(
    tags=["Users"]
)

class UserORM(BaseModel):
    email: EmailStr
    password: str
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    class Config:
        orm_mode= True

pwd_context= CryptContext(schemes=["bcrypt"], deprecated="auto") #For more security reasons we can store this in a seperate file and import it here.

@router.post("/users",status_code=status.HTTP_201_CREATED, response_model=list[UserResponse])
def create_user(payload: UserORM,db: Session = Depends(get_db)):
    secure_password = pwd_context.hash(payload.password)
    payload.password= secure_password
    new_user = tables.User(**payload.dict()) 
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return [new_user] #{"message": "User created successfully", "user": new_user}

@router.get("/users",response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    users= db.query(tables.User).all()
    return users

@router.get("/users/{id}",response_model=UserResponse)
def get_user_byid(id : int,db: Session = Depends(get_db)):
    user = db.query(tables.User).filter(tables.User.id==id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found in the list or database.")
    return user

@router.delete("/users/delete/{id}")
def del_user(id : int,db: Session = Depends(get_db)):
    user = db.query(tables.User).filter(tables.User.id==id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found in the list or database.")
    db.delete(user)
    db.commit()
    return {"message": f"user with id {id} has been deleted successfully.", "deleted_user": str(user)}