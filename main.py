from fastapi import FastAPI,status,HTTPException
#from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
app= FastAPI()

class About(BaseModel):
    Title: str
    Content: str = ""
    Id: Optional[int] = None

@app.get("/posts")
def root():
    return {"message": list_of_posts}

list_of_posts=[{"Title":"first title", "Content":"first content", "Id": 1},{"Title":"second title", "Content":"second content", "Id": 2}]

# getlatest has to be above get_post because it is more specific and will be matched first.
@app.get("/posts/latest")
def get_latest_post():
    return {"message": f"the latest post is {list_of_posts[-1]}"}

@app.get("/posts/{id}")
def get_post(id: int):
    for i in list_of_posts:
        if int(i["Id"])==id:
            print(list_of_posts)
            return {"message": f"the called post with ID {id} is {i}"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found in the list or database.")

@app.post("/create_posts",status_code=status.HTTP_201_CREATED)
def create_post(payload: About):
    print(payload.Title)
    payload.Id= randrange(1, 10000)
    list_of_posts.append(payload.dict())
    return {"message": "Post created successfully", "title": f"{payload.Title}" , "content": f"{payload.Content}" , "id": f"{payload.Id}" , "Dict version": f"{payload.dict()}"} 

@app.delete("/posts/{id}")
def del_post(id : int):#During deletion status code should be 204 but we are returning a message so we will use 200.
    for i in range(len(list_of_posts)):
        if list_of_posts[i]["Id"]==id:
            val= list_of_posts[i]
            del list_of_posts[i]
            return {"message": f"post with id {id} has been deleted successfully.", "deleted_post": val}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found in the list or database.")

@app.put("/posts/{id}")
def update_post(id: int, payload: About):
    for i in range(len(list_of_posts)):
        if list_of_posts[i]["Id"]==id:
            list_of_posts[i]= payload.dict()
            list_of_posts[i]["Id"]=id #Id should not be updated so we are setting it back to the original id.
            return {"message": f"post with id {id} has been updated successfully.", "updated_post": list_of_posts[i]}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found in the list or database.")