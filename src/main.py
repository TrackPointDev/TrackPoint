import os
import uvicorn

from database.setup import setup_database
from database.manager import DatabaseManager
from database.models import Task
from secret_manager import access_secret_version
from webhook import Webhook

from typing import Annotated, Union

from fastapi import FastAPI, HTTPException, Header
from fastapi import Request

from routers import tasks

from src import config, db

# Initialize FastAPI application
app = FastAPI(title="TrackPoint-Backend", description="API for TrackPoint's backend.")
app.include_router(tasks.router)

#TODO create a config or env file for these



@app.post("/tasks")
async def create_task(task: Task):
    """
    Creates a new task in the Firestore database.

    Args:
        task (Task): The task to be created.
    Returns:
        dict: A dictionary containing the status and message of the operation.
    """
    task_json = task.model_dump(mode='json')
    print(f"Received task: {task_json}")

    try:
        db.add_task(task_json)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

    return {"status": 200, "message": "Task created successfully."}

@app.get("/tasks")
async def get_tasks(taskID: Annotated[int | str | None, Header()] = None) -> Union[dict, list]:
    """
    Get either a specific task or the entire list of tasks from the Firestore database.

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
            return db.get_task(taskID)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    try:
        return db.get_tasks_list()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@app.put("/tasks")
async def update_task(taskID: Annotated[int | str | None, Header()], task: Task):
    """
    Updates a given task in the Firestore database.

    Args:
        taskID (int or str): The task to be updated. Can be either the taskID (int) or the task title (str).
        task (Task): The task to be created.
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
            db.update_task(taskID, task.model_dump(mode='json'))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

    return {"message": "Task updated"}

@app.delete("/tasks")
async def delete_task(taskID: Annotated[int | str, Header()]):
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
        db.delete_task(taskID)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

    return {"message": "Task deleted"}

@app.post("/")
async def listener(request: Request = None):
    payload = await request.json()
    print(f"Received payload: {payload}")

    return {"status": 200, "message": "Webhook event processed successfully."}


def main():
    try:
        uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    except KeyboardInterrupt:
        print("Closing listener")


if __name__ == "__main__":
    main()
    

