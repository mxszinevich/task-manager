from fastapi import APIRouter, Depends
from starlette import status

from api.dependencies.users import get_active_user
from common import ForbiddenException, NotFoundException
from db.models import Task, User
from db.repositories.tasks import TasksRepository
from shemas import TaskCreateIn, TaskCreateOut
from shemas.tasks import TaskDetail, TaskUpdate

router = APIRouter()


@router.post("/", summary="Создание задачи", response_model=TaskCreateOut)
async def task_create(
    task: TaskCreateIn, user: User = Depends(get_active_user), task_repo: TasksRepository = Depends()
):
    task = task.copy(update={"user_id": user.id})
    created_task = await task_repo.create(task)
    return created_task


@router.get("/", summary="Список задач", response_model=list[TaskDetail])
async def task_list(user: User = Depends(get_active_user), task_repo: TasksRepository = Depends()):
    tasks = await task_repo.filters(user_id=user.id)
    return tasks


@router.get("/{task_id}", summary="Детализация задачи", response_model=TaskDetail)
async def task_detail(task_id: int, user: User = Depends(get_active_user), task_repo: TasksRepository = Depends()):
    task: Task = await task_repo.get_object(id=task_id, user_id=user.id)
    return task


@router.delete("/{task_id}", summary="Удаление задачи", status_code=status.HTTP_204_NO_CONTENT)
async def task_delete(task_id: int, user: User = Depends(get_active_user), task_repo: TasksRepository = Depends()):
    task: Task | None = await task_repo.get_object(id=task_id)
    if task is None:
        raise NotFoundException(id=task_id)

    if task.user_id != user.id and not user.is_superuser:
        raise ForbiddenException

    await task_repo.delete(id=task_id)


@router.put("/{task_id}", summary="Обновление задачи")
async def task_update(
    task_id: int, task: TaskUpdate, user: User = Depends(get_active_user), task_repo: TasksRepository = Depends()
):
    task_in_db: Task | None = await task_repo.get_object(id=task_id)
    if task_in_db is None:
        raise NotFoundException(id=task_id)

    if task_in_db.user_id != user.id:
        raise ForbiddenException

    await task_repo.update(filter_params={"id": task_id}, update_values=task.dict(exclude_none=True))
    return task_in_db