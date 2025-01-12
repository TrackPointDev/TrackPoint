from typing import Annotated, Union
from fastapi import APIRouter, HTTPException, Header, Request, Depends
from fastapi_utils.cbv import cbv

from database.models import Task
from Google import sheet_utils

router = APIRouter(
    prefix="/epics/tasks",
    tags=["Tasks"],
    responses={404: {"description": "Not found"}},
)

@cbv(router)
class TaskHandler:
    def __init__(self, request: Request):
        self.logger = request.app.state.logger
        self.db = request.app.state.db
        self.sheet = sheet_utils.SheetUtils(request)

    @router.post("/add")
    async def create_task(self, task: Task = None, epicID: Annotated[str, Header()] = None):
        """
        Creates a new task within an epic and stores it on the associated sheet as well as the Firestore DB.

        Args:
            task (Task): The task to be created.
        Returns:
            dict: A dictionary containing the status and message of the operation.
        """
        task_json = task.model_dump(mode='json')
        print(f"Received task: {task_json}")

        try:
            epic = self.db.get_epic(identifier=epicID)
            self.db.add_task(task, epic.title)
            print("Writing to sheet...")
            self.sheet.add_task(task, spreadsheetID=epic.spreadsheetId)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

        return {"status": 200, "message": f"Task created successfully. Added to Epic '{epic.title}.'"}

    @router.get("/get")
    async def get_tasks(self, taskID: Annotated[int | str | None, Header()] = None, epicID: Annotated[str, Header()] = None) -> Union[dict, list]:
        """
        Get either a specific task or the entire list of tasks in the Firestore database.

        Args:
            taskID (int or str): Optional ID for the task to be retrieved. If none is provided, all tasks will be returned.
        Returns:
            task (dict or list): A dictionary containing the task data if a taskID is provided, or a list of all tasks.
        Raises:
            HTTPException: If an error occurs during the fetch operation, it will be caught and a 500 error will be raised.
        """

        try:
            epic = self.db.get_epic(identifier=epicID)
            if taskID is None:
                return self.db.get_tasks_list(epic.title)
            elif taskID is not None:
                return self.db.get_task(taskID, epic.title)
            else:   
                raise HTTPException(status_code=404, detail="Please provide a valid task ID.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

    @router.put("/update")
    async def update_task(self, task: Task = None, epicID: Annotated[str, Header()] = None):
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

        try:
            # retreive the epic associated with the task.
            epic = self.db.get_epic(identifier=epicID)
            self.db.update_task(task.issueID, epic.title)
            self.sheet.update_task(task, epic.spreadsheetId)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

        return {"status": 200, "message": f"Task updated successfully. Updated DB in Epic '{epic.title} and updated in sheet.'"}

    @router.delete("/delete")
    async def delete_task(self, task: Task = None, epicID: Annotated[str, Header()] = None):
        """
        Delete a specific task in the Firestore database.

        Args:
            taskID (int or str): The task to be deleted. Cen be either the taskID (int) or the task title (str).
        Returns:
            dict: A message indicating the status of the operation.
        Raises:
            HTTPException: If an error occurs during the delete operation, it will be caught and a 500 error will be raised.
        """

        try:
            # retreive the epic associated with the task.
            epic = self.db.get_epic(identifier=epicID)
            self.db.delete_task(task, epic.title)
            self.sheet.remove_task(task, epic.spreadsheetId)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

        return {"message": "Task deleted"}