from typing import Any, Dict, Optional
from fastapi import FastAPI, Request, HTTPException
from database.models import Epic, Task
from typing import Literal, Union


class PluginManager:
    def __init__(self, app: FastAPI):
        self.app = app
        self.db = app.state.db
        self.logger = app.state.logger
    
    endpoint = Literal["epic_setup", "epic_update", "epic_delete", "task_add", "task_update", "task_delete"]
    URLS: dict[endpoint, str] = {
    "epic_setup": "https://trackpoint-github-gcf-87527377987.europe-west3.run.app/epic/setup",
    "epic_update": "https://trackpoint-github-gcf-87527377987.europe-west3.run.app/epic/update",
    "epic_delete": "https://trackpoint-github-gcf-87527377987.europe-west3.run.app/epic/delete",
    "task_add": "https://trackpoint-github-gcf-87527377987.europe-west3.run.app/task/add",
    "task_update": "https://trackpoint-github-gcf-87527377987.europe-west3.run.app/task/update",
    "task_delete": "https://trackpoint-github-gcf-87527377987.europe-west3.run.app/task/delete",
    }
    async def post_to_plugin(self, epic: Epic, method: endpoint, task: Optional[Task] = None) -> Dict[str, Any]:
        client = self.app.state.client

        if task and method in ["epic_setup", "epic_update", "epic_delete"]:
            raise ValueError("Task object passed to an epic method.")

        if method in ["task_add", "task_update", "task_delete"]:
            self.logger.info(f"Crafting task payload: '{task.title}', with method: '{method}'")
            payload = task.model_dump(mode='json')
            payload.update({"repoOwner": epic.repoOwner, "repoName": epic.repoName, "installationID": epic.installationID})
        else:
            self.logger.info(f"Crafting epic payload: '{epic.title}', with method: '{method}'")
            payload = epic.model_dump(mode='json')
        
        self.logger.info(f"Sending payload to {self.URLS[method]}")
        url = self.URLS[method]
    
        try:
            self.app.state.logger.info(f"Sending payload: '{payload}' to '{url}'")
            response = await client.post(url, json=payload)
            response.raise_for_status()  # throw an error if not 2xx
        except Exception as e:
            raise HTTPException(e)
        
        if isinstance(response, dict): # Sometimes response returns <Response [200 OK]> instead of a dict. This handles that.
            self.app.state.logger.info(f"Response: {response.json()}")
            return response.json()
        else:
            return {"status": 200, "message": response}


