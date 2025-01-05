from typing import Annotated, Union
from fastapi import APIRouter, HTTPException, Header, Request

from database.manager import DatabaseManager
from database.models import Task


router = APIRouter(
    prefix="/epics/tasks",
    tags=["Tasks"],
    responses={404: {"description": "Not found"}},
)


class TaskHandler:
    def __init__(self, request: Request):
        self.client = request.app.state.client
        self.logger = request.app.state.logger
        self.db = request.app.state.db

    @router.post("")
    async def create_task(self, task: Task):
        """
        Creates a new task in the Firestore database.

        Args:
            task (Task): The task to be created.
        Returns:
            dict: A dictionary containing the status and message of the operation.
        """
        task_json = task.model_dump(mode='json')
        print(f"Received task: {task_json}")

        response = self.client.post("https://example.org", json=task_json)
        print(f"Response: {response}")

        try:
            self.db.add_task(task_json)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

        return {"status": 200, "message": "Task created successfully."}

    @router.get("")
    async def get_tasks(self, taskID: Annotated[int | str | None, Header()] = None) -> Union[dict, list]:
        """
        Get either a specific task or the entire list of tasks in the Firestore database.

        Args:
            taskID (int or str): Optional ID for the task to be retrieved. If none is provided, all tasks will be returned.
        Returns:
            task (dict or list): A dictionary containing the task data if a taskID is provided, or a list of all tasks.
        Raises:
            HTTPException: If an error occurs during the fetch operation, it will be caught and a 500 error will be raised.
        """

        if taskID:
            # For some reason, headers are casted to strings even when an int is passed. This is a workaround.
            if isinstance(taskID, str) and taskID.isdigit():
                taskID = int(taskID)
            try:
                return self.db.get_task(taskID)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
        try:
            return self.db.get_tasks_list()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

    @router.put("")
    async def update_task(self, taskID: Annotated[int | str | None, Header()], task: Task):
        """
        Updates a given task in the Firestore database.

        Args:
            taskID (int or str): The task to be updated. Can be either the taskID (int) or the task title (str).
            task (Task): Entire new Task object containing the new values. Current implementation does not support partial updates.
        Returns:
            dict: A dictionary containing the status and message of the operation.
        Raises:
            HTTPException: If an error occurs during the update operation, it will be caught and a 500 error will be raised.
        """

        if taskID:
            # For some reason, headers are casted to strings even when an int is passed. This is a workaround.
            if isinstance(taskID, str) and taskID.isdigit():
                taskID = int(taskID)
            try:
                self.db.update_task(taskID, task.model_dump(mode='json'))
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

        return {"message": "Task updated"}

    @router.delete("")
    async def delete_task(self, taskID: Annotated[int | str, Header()]):
        """
        Delete a specific task in the Firestore database.

        Args:
            taskID (int or str): The task to be deleted. Cen be either the taskID (int) or the task title (str).
        Returns:
            dict: A message indicating the status of the operation.
        Raises:
            HTTPException: If an error occurs during the delete operation, it will be caught and a 500 error will be raised.
        """

        if isinstance(taskID, str) and taskID.isdigit():
            taskID = int(taskID)
        try:
            self.db.delete_task(taskID)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

        return {"message": "Task deleted"}