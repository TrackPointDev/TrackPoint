import httpx
from typing import Any, Dict, Optional
from fastapi import FastAPI, Request, HTTPException
from database.models import Epic, Task
from typing import Literal, Union


class PluginManager:
    def __init__(self, app: FastAPI):
        self.app = app
        self.db = app.state.db
    
    endpoint = Literal["setup", "update", "task", "test"]
    URLS: dict[endpoint, str] = {
    "setup": "https://trackpoint-github-gcf-87527377987.europe-west3.run.app/epic/setup",
    "update": "https://trackpoint-github-gcf-87527377987.europe-west3.run.app/epic/update",
    "task": "https://trackpoint-github-gcf-87527377987.europe-west3.run.app/task/update",
    }
    async def post_to_plugin(self, payload: Union[Epic, Task], method: endpoint) -> Dict[str, Any]:
        client = self.app.state.client

        if isinstance(payload, Task) and (method == "update" or method == "setup"):
            raise ValueError("Task object cannot be used with 'update' or 'setup' methods.")
        else:
            url = self.URLS[method]
    
        try:
            response = await client.post(url, json=payload.model_dump(mode='json'))
            #response.raise_for_status()  # throw an error if not 2xx
        except Exception as e:
            raise HTTPException(e)
        self.assign_issue_id(response.json(), payload)
        print(f"Response: {response}")
        return response.json()

    def assign_issue_id(self, response: dict, payload: Union[Epic, Task]) -> Task:
        if isinstance(payload, Task):
            updated_task = Task(
                title = response.get("title", payload.title),
                comments = payload.comments,
                description = payload.description,
                issueID = response.get("number", payload.issueID),
                priority = payload.priority,
                story_point = payload.story_point)
            self.db.update_task(updated_task.title, updated_task.model_dump(mode='json'))
            return {"status": 200, "message": "Task ID updated successfully."}
        elif isinstance(payload, Epic):
            for item in response:
                for task in payload.tasks:
                    if task.title == item.get("title"):
                        task.issueID = item.get("number")
            self.db.update_epic(payload.title, payload.model_dump(mode='json'))
            return {"status": 200, "message": "Issue IDs assigned successfully."}

