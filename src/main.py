import uvicorn

from database.setup import setup_database
from database.manager import DatabaseManager
from database.models import Task
from secret_manager import access_secret_version
from webhook import Webhook

from typing import Annotated, Union

from fastapi import FastAPI, HTTPException, Header
from fastapi import Request


# Initialize FastAPI application
app = FastAPI(title="TrackPoint-Backend", description="API for TrackPoint's backend.")

#TODO create a config or env file for these
class Config:
    def __init__(self):
        self.spreadsheet_id = "1o5JoaPwq7uP9oYs9KuhFBc9MJP6JybIhaLRUscgame8"
        self.db_collection = "epics"
        self.db_document = "showcase"
        self.owner = "TrackPointDev"
        self.repo = "TrackPointTest"
        self.project_id = "trackpointdb"
        self.gh_secret_id = "hamsterpants-github-pat"
        self.ado_secret_id = "az-devops-pat"
        self.ngrok_secret_id = "NGROK_AUTHTOKEN"
        self.gh_version_id = "latest"

config = Config()

def initialize_webhook():
    """
    Method to initialize a Webhook instance. Should be deprecated once back-end api is hosted on a cloud platform.
    """
    
    webhook_instance = Webhook(
        config.db_collection, 
        config.db_document, 
        config.project_id, 
        config.gh_version_id, 
        config.ngrok_secret_id)
    return webhook_instance

webhook_instance = initialize_webhook()
db = DatabaseManager(config.db_collection, config.db_document)

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
    Get a list of tasks or a single task based on the task_id.
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
    # Update task based on source
    return {"message": "Task updated"}

@app.delete("/tasks")
async def delete_task(taskID: Annotated[int | str, Header()]):
    # Delete task logic here

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

    await webhook_instance.webhook_update_db(payload)

    return {"status": 200, "message": "Webhook event processed successfully."}


def main():
    try:
        uvicorn.run(app, host="0.0.0.0", port=5000)
    except KeyboardInterrupt:
        print("Closing listener")


if __name__ == "__main__":
    main()
    

