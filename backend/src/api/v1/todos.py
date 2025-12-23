from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List
from datetime import datetime

from core.database import get_db
from models import User, Todo
from schemas.todo import TodoCreate, TodoUpdate, TodoResponse
from api.dependencies import UserIdDep

router = APIRouter(prefix="/todos", tags=["todos"])


@router.post("", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo_data: TodoCreate,
    user_id: UserIdDep,
    db: AsyncSession = Depends(get_db),
):
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    new_todo = Todo(
        title=todo_data.title,
        description=todo_data.description,
        due_date=todo_data.due_date,
        user_id=user.id,
    )
    db.add(new_todo)
    await db.commit()
    await db.refresh(new_todo)

    return new_todo


@router.get("", response_model=List[TodoResponse])
async def get_todos(
    user_id: UserIdDep,
    skip: int = 0,
    limit: int = 20,
    completed_only: bool = False,
    db: AsyncSession = Depends(get_db),
):
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    if not user.couple_id:
        result = await db.execute(
            select(Todo)
            .where(Todo.user_id == user_id)
            .order_by(desc(Todo.created_at))
            .offset(skip)
            .limit(limit)
        )
    else:
        result = await db.execute(
            select(Todo)
            .where(User.couple_id == user.couple_id)
            .order_by(desc(Todo.created_at))
            .offset(skip)
            .limit(limit)
        )

    todos = result.scalars().all()

    if completed_only:
        todos = [t for t in todos if t.is_completed]

    return list(todos)


@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(todo_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Todo).where(Todo.id == todo_id))
    todo = result.scalar_one_or_none()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="待办事项不存在"
        )
    return todo


@router.put("/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: int,
    todo_data: TodoUpdate,
    user_id: UserIdDep,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Todo).where(Todo.id == todo_id))
    todo = result.scalar_one_or_none()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="待办事项不存在"
        )

    if todo.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限编辑此待办事项"
        )

    if todo_data.title is not None:
        todo.title = todo_data.title
    if todo_data.description is not None:
        todo.description = todo_data.description
    if todo_data.is_completed is not None:
        todo.is_completed = todo_data.is_completed
        if todo.is_completed and todo.completed_at is None:
            todo.completed_at = datetime.utcnow()
        elif not todo.is_completed:
            todo.completed_at = None
    if todo_data.due_date is not None:
        todo.due_date = todo_data.due_date

    await db.commit()
    await db.refresh(todo)

    return todo


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: int,
    user_id: UserIdDep,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Todo).where(Todo.id == todo_id))
    todo = result.scalar_one_or_none()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="待办事项不存在"
        )

    if todo.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限删除此待办事项"
        )

    await db.delete(todo)
    await db.commit()

    return None
