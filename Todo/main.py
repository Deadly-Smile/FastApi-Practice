from datetime import datetime
from typing import Optional
from fastapi import FastAPI, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from utill import ThrowException
import models
from database import engine, SessionLocal
from auth import get_current_user

app = FastAPI()
models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def varify_user(user):
    if user is None:
        raise ThrowException(401, "Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})


class TodoRequest(BaseModel):
    title: str = Field(max_items=63)
    description: Optional[str]
    priority: int = Field(1, ge=1, le=5, description="value must be between 1 and 5")
    complete: Optional[bool] = Field(False)


@app.get("/create-database")
async def create_database(db: Session = Depends(get_db)):
    return db.query(models.Todos).all()


@app.get("/todo")
async def get_todos(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    varify_user(user)
    todos = db.query(models.Todos).filter(models.Todos.owner_id == user.get('id')).all()
    if not todos:
        return {"todos": []}
    return {"todos": todos}


@app.post("/todo")
async def create_todo(todo: TodoRequest, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    varify_user(user)
    db_todo = models.Todos(title=todo.title, description=todo.description, priority=todo.priority,
                           complete=todo.complete, created_at=datetime.now(), owner_id=user.get("id"))
    db.add(db_todo)
    db.commit()
    if not db_todo:
        raise ThrowException(404, "Something is wrong")
    return {"todo": db_todo}


@app.put("/todo/{todo_id}")
async def update_todo(todo_id: int, todo: TodoRequest, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    varify_user(user)
    db_todo = (db.query(models.Todos).filter(models.Todos.id == todo_id)
               .filter(models.Todos.owner_id == user.get("id")).first())
    if todo is None:
        raise ThrowException(404, "Todo not found")

    db_todo.title = todo.title
    db_todo.description = todo.description
    db_todo.priority = todo.priority
    db_todo.complete = todo.complete
    db.add(db_todo)
    db.commit()

    return db_todo


@app.get("/todo/{todo_id}")
async def get_todo(todo_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise ThrowException(401, "Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    todo = (db.query(models.Todos).filter(models.Todos.id == todo_id)
            .filter(models.Todos.owner_id == user.get("id")).first())
    if todo is None:
        raise ThrowException(404, "Todo not found")
    return todo


@app.delete("/todo/{todo_id}")
async def delete_todo(todo_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    varify_user(user)
    if (db.query(models.Todos).filter(models.Todos.id == todo_id)
            .filter(models.Todos.owner_id == user.get("id")).first() is None):
        raise ThrowException(404, "Todo not found")
    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()

    db.commit()
    return {
        "status": 201,
        "transaction": "Successful"
    }


@app.get("/todos/user")
async def get_all_by_user(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    varify_user(user)
    return db.query(models.Todos).filter(models.Todos.owner_id == user.get("id")).all()
