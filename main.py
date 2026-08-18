from fastapi import FastAPI,status,HTTPException , Depends
#from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os
from sqlalchemy.orm import Session
from database import get_db, engine
import models

models.Base.metadata.create_all(bind=engine)

app= FastAPI()
load_dotenv()
DB_PASSWORD= os.getenv("DB_PASSWORD")

#dependency

        
class About(BaseModel):
    title: str
    content: str 
    published: Optional[bool]= True

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



@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    p= db.query(models.Post).all() #p var is a query and .all() executes query.Use the class name to query the table instead of table name. 
    #Class name is Post and table name is posts_alchaemy.Post is used to query the table as it is mapped to the table using __tablename__
    return {"message": p}

@app.post("/sqlalchemy/create",status_code=status.HTTP_201_CREATED)
def create_post_sqlalchemy(payload: About, db: Session = Depends(get_db)):
    new_post = models.Post(**payload.dict()) #**payload.dict() unpacks dictionary and passes key-value as arguments to the Post class constructor.
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"message": new_post}

@app.get("/sqlalchemy/{id}")
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found in the list or database.")
    return {"message": post}


@app.delete("/sqlalchemy/{id}")
def del_post(id : int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found in the list or database.")
    db.delete(post)
    db.commit()
    return {"message": f"post with id {id} has been deleted successfully.", "deleted_post": post}

@app.put("/sqlalchemy/{id}")
def update_post(id: int, payload: About, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post=post_query.first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found in the list or database.")
    post_query.update(payload.dict(), synchronize_session=False) #synchronize_session=False used to avoid the overhead of synchronizing session with the database after the update.
    db.commit()
    db.refresh(post)
    return {"message": f"post with id {id} has been updated successfully.", "updated_post": post}

#Everything above this line is for sqlalchemy and everything below this line is for psycopg2.
@app.get("/posts")
def root():
    cursor.execute("SELECT * FROM posts")
    list_of_posts= cursor.fetchall()
    return {"message": list_of_posts}

list_of_posts=[{"title":"first title", "content":"first content", "id": 1},{"title":"second title", "content":"second content", "id": 2}]

# getlatest has to be above get_post because it is more specific and will be matched first.
@app.get("/posts/latest")
def get_latest_post():
    #return {"message": f"the latest post is {list_of_posts[-1]}"}
    cursor.execute("SELECT * FROM posts ORDER BY id DESC LIMIT 1")
    latest_post= cursor.fetchone()
    return {"message": f"the latest post is {latest_post}"}

@app.get("/posts/{id}")
def get_post(id: int): #In the query we are passing id as a string but in the function we are accepting it as an integer even tho in the path its a string ,
    # and we are converting it to integer in the function so that we can compare it with the id in the list which is an integer.
    # If we don't convert it to integer then we will get a type error where in a string of char is also validated as id
    '''for i in list_of_posts:
        if int(i["id"])==id:
            print(list_of_posts)
            return {"message": f"the called post with ID {id} is {i}"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found in the list or database.")'''
    
    cursor.execute("SELECT * FROM posts WHERE id= %s", (str(id),)) #As the query is a string we need to convert the id to string. 
    #Also, we need to pass the id as a tuple so we need to add a comma after str(id).
    post= cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found in the list or database.")
    return {"message": f"the called post with ID {id} is {post}"}

@app.post("/create_posts",status_code=status.HTTP_201_CREATED)
def create_post(payload: About):
    '''print(payload.title)
    payload.id= randrange(1, 10000)
    list_of_posts.append(payload.dict())
    return {"message": "Post created successfully", "title": f"{payload.title}" , "content": f"{payload.content}" , "id": f"{payload.id}" , "Dict version": f"{payload.dict()}"}'''

    cursor.execute("INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *", (payload.title, payload.content, payload.published))
    new_post= cursor.fetchone()
    conn.commit() #Saves the staged changes that are made above in the database. If we don't commit then the changes will not be saved in the database.
    return {"message": "Post created successfully", "post": new_post}
@app.delete("/posts/{id}")
def del_post(id : int):#During deletion status code should be 204 but we are returning a message so we will use 200.
    '''for i in range(len(list_of_posts)):
        if list_of_posts[i]["id"]==id:
            val= list_of_posts[i]
            del list_of_posts[i]
            return {"message": f"post with id {id} has been deleted successfully.", "deleted_post": val}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found in the list or database.")'''
    cursor.execute("DELETE FROM posts WHERE id= %s RETURNING *", (str(id),))
    deleted_post= cursor.fetchone()
    conn.commit()
    if not deleted_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found in the list or database.")
    return {"message": f"post with id {id} has been deleted successfully.", "deleted_post": deleted_post}

@app.put("/posts/{id}")
def update_post(id: int, payload: About):
    '''for i in range(len(list_of_posts)):
        if list_of_posts[i]["id"]==id:
            list_of_posts[i]= payload.dict()
            list_of_posts[i]["id"]=id #Id should not be updated so we are setting it back to the original id.
            return {"message": f"post with id {id} has been updated successfully.", "updated_post": list_of_posts[i]}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found in the list or database.")'''

    cursor.execute("UPDATE posts SET title= %s, content= %s, published= %s WHERE id= %s RETURNING *", (payload.title, payload.content, payload.published, str(id)))
    updated_post= cursor.fetchone()
    conn.commit()  
    if not updated_post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found in the list or database.")
    return {"message": f"post with id {id} has been updated successfully.", "updated_post": updated_post}