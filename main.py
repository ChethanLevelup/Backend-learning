from fastapi import FastAPI,HTTPException
from typing import List, Optional
from enum import IntEnum
from pydantic import BaseModel,Field
from math import ceil

app = FastAPI()

class Priority(IntEnum):
    LOW = 3
    MEDIUM = 2
    HIGH = 1

class TodoBase(BaseModel):
    todo_name: str = Field(...,min_length=3,max_length=512,description="Name of the todo")
    todo_description: str = Field(...,description="Description of the todo")
    priority: Priority = Field(default=Priority.LOW,description="Priority of the todo")

class TodoCreate(TodoBase):
    ...

class Todo(TodoBase):
    todo_id: int = Field(...,description="Unique identifier of the todo")

class TodoUpdate(BaseModel):
    todo_name: Optional[str] = Field(None,min_length=3,max_length=512,description="Name of the todo")
    todo_description: Optional[str] = Field(None,description="Description of the todo")
    priority: Optional[Priority] = Field(None,description="Priority of the todo")

class Pagination(BaseModel):
    items : List[Todo]
    totalItems : int
    totalPages : int
    currentPage : int
    pageSize : int



all_todos = [
    Todo(todo_id=1,todo_name="Sports",todo_description="Go to the gym",priority=Priority.HIGH),
    Todo(todo_id=2, todo_name="Read", todo_description="Read 10 pages",priority=Priority.MEDIUM),
    Todo(todo_id=3, todo_name="Shop", todo_description="Go shopping",priority=Priority.LOW),
    Todo(todo_id=4, todo_name="Study", todo_description="Study for exam",priority=Priority.MEDIUM),
    Todo(todo_id=5, todo_name="Meditate", todo_description="Meditate 20 minutes",priority=Priority.LOW)
]

@app.get("/todos",response_model=Pagination)
def all_list(first_n:int = 3,page_no:int = 1):
    if(page_no<1 or first_n<1):
        raise HTTPException(status_code=400,detail="Invalid Pagination values")
    
    total_items = len(all_todos)
    total_pages = ceil(total_items/first_n)
    if(page_no>total_pages):
        raise HTTPException(status_code=404,detail="Page not found")
    start = (page_no-1)*first_n
    end = start+first_n
    items = all_todos[start:end]
    return {
        "items" : items,
        "totalItems" : total_items,
        "totalPages" : total_pages,
        "currentPage" : page_no,
        "pageSize" : first_n
    }
    

@app.get("/todos/{todo_get_id}",response_model=Todo)
def get_list(todo_get_id:int):
    for todo in all_todos:
        if(todo.todo_id == todo_get_id):
            return todo
    raise HTTPException(status_code=404,detail="Todo Not Found")

@app.post("/todos",response_model=Todo)
def create_todo(todo: TodoCreate):
    new_todo_id: int = max((todo.todo_id) for todo in all_todos) + 1
    new_todo = Todo(
        todo_id = new_todo_id,
        todo_name = todo.todo_name,
        todo_description = todo.todo_description,
        priority = todo.priority
    )
    all_todos.append(new_todo)
    return new_todo


@app.put("/todos/{todo_update_id}",response_model=Todo)
def update_todo(todo_update_id: int,updated_todo: TodoUpdate):
    for todo in all_todos:
        if(todo.todo_id == todo_update_id):
            if updated_todo.todo_name is not None:
                todo.todo_name = updated_todo.todo_name
            if updated_todo.todo_description is not None:
                todo.todo_description = updated_todo.todo_description
            if updated_todo.priority is not None:
                todo.priority = updated_todo.priority
            return todo
    raise HTTPException(status_code=404,detail="Todo not found")


@app.delete("/todos/{todo_delete_id}",response_model=Todo)
def delete_todo(todo_delete_id:int):
    for index,todo in enumerate(all_todos):
        if(todo.todo_id==todo_delete_id):
            deleted_todo = all_todos.pop(index)
            return deleted_todo
    raise HTTPException(status_code=404,detail="Todo not found")
