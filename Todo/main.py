from datetime import datetime
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse

import models
from database import engine, SessionLocal

app = FastAPI()
models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class TodoRequest(BaseModel):
    title: str = Field(max_items=63)
    description: Optional[str]
    priority: int = Field(1, ge=1, le=5, description="value must be between 1 and 5")
    complete: Optional[bool] = Field(False)


def ThrowException(status_code: int, detail: str, headers: str = None):
    if headers is None:
        raise HTTPException(status_code=status_code, detail=detail)
    else:
        raise HTTPException(status_code=status_code, detail=detail, headers={"X-Header-Error": headers})


def Response(content: object, status_code: int, headers: str = None):
    if headers is None:
        return JSONResponse(content=content, status_code=status_code)
    else:
        return JSONResponse(content=content, status_code=status_code, headers={"X-Header-Info": headers})


@app.get("/create-database")
async def create_database(db: Session = Depends(get_db)):
    return db.query(models.Todos).all()


@app.post("/todo")
async def create_todo(todo: TodoRequest, db: Session = Depends(get_db)):
    db_todo = models.Todos(title=todo.title, description=todo.description, priority=todo.priority,
                           complete=todo.complete, created_at=datetime.now())
    db.add(db_todo)
    db.commit()
    # json.dump(db_todo.__dict__)
    return db_todo


@app.put("/todo/{todo_id}")
async def update_todo(todo_id: int, todo: TodoRequest, db: Session = Depends(get_db)):
    db_todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
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
async def get_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if todo is None:
        raise ThrowException(404, "Todo not found")
    return todo


@app.delete("/todo/{todo_id}")
async def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    if db.query(models.Todos).filter(models.Todos.id == todo_id).first() is None:
        raise ThrowException(404, "Todo not found")
    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()

    db.commit()
    return {
        "status": 201,
        "transaction": "Successful"
    }
