from fastapi import status,HTTPException , Depends, APIRouter
from pydantic import BaseModel
from database import get_db
from sqlalchemy.orm import Session #, relationship
import tables
from routers import jwts , user
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os

load_dotenv()
DB_PASSWORD= os.getenv("DB_PASSWORD")

router = APIRouter(
    tags=["Posts"]
)

class About(BaseModel):
    title: str
    content: str 
    published: Optional[bool]= True
    #user_id : int we dont add this here because its not something that user types in, its something that has to authenticated,ie. after login

try:
    conn = psycopg2.connect(
    host="localhost",
    database="fastapibasic",
    user="postgres",
    password=DB_PASSWORD,
    cursor_factory=RealDictCursor
    )
    cursor = conn.cursor()
    print("Database connection was successful")
except Exception as error:
    print(f"Connecting to database failed due to {error}")

class PostResponse(BaseModel):
    title: str
    content: str 
    #user_id : int
    owner : user.UserResponse
    class Config: #we write this class to tell pydantic that the data we are returning is not a dictionary but an ORM model object and we want to convert it to a dictionary.
        orm_mode= True #orm_mode is renamed to from_attributes



@router.get("/sqlalchemy",response_model=list[PostResponse])
def test_posts(db: Session = Depends(get_db),user_id : int = Depends(jwts.get_cur_user),limit:int=100,search : Optional[str] ="" ):
    p= db.query(tables.Post).filter(tables.Post.title.contains(search)).limit(limit).all() #p var is a query and .all() executes query.Use the class name to query the table instead of table name. 
    #Class name is Post and table name is posts_alchaemy.Post is used to query the table as it is mapped to the table using __tablename__
    return p

@router.post("/sqlalchemy/create",status_code=status.HTTP_201_CREATED)
def create_post_sqlalchemy(payload: About, db: Session = Depends(get_db),user_id : int = Depends(jwts.get_cur_user)):
    new_post = tables.Post(user_id = user_id.id, **payload.dict()) #**payload.dict() unpacks dictionary and passes key-value as arguments to the Post class constructor.
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"message": new_post}

@router.get("/sqlalchemy/{id}")
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(tables.Post).filter(tables.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found in the list or database.")
    return {"message": post}


@router.delete("/sqlalchemy/{id}")
def del_post(id : int, db: Session = Depends(get_db),user_id : int = Depends(jwts.get_cur_user)):
    post = db.query(tables.Post).filter(tables.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found in the list or database.")
    if post.user_id != user_id.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"id {user_id.id} Not authorized to perform requested action.")
    db.delete(post)
    db.commit()
    return {"message": f"post with id {id} has been deleted successfully.", "deleted_post": post}

@router.put("/sqlalchemy/{id}")
def update_post(id: int, payload: About, db: Session = Depends(get_db),user_id : int = Depends(jwts.get_cur_user)):
    post_query = db.query(tables.Post).filter(tables.Post.id == id)
    post=post_query.first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found in the list or database.")
    if post.user_id != user_id.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"id {user_id.id} Not authorized to perform requested action.")
    post_query.update(payload.dict(), synchronize_session=False) #synchronize_session=False used to avoid the overhead of synchronizing session with the database after the update.
    db.commit()
    db.refresh(post)
    return {"message": f"post with id {id} has been updated successfully.", "updated_post": post}