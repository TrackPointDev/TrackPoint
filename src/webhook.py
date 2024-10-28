import ngrok
import time
import re
import os
import json
import uvicorn
from fastapi import FastAPI, APIRouter

from Google.sheets import Task
from epics.database_epic import database_epic
from secret_manager import access_secret_version
from database.manager import DatabaseManager
from fastapi import Request

class Webhook:
    def __init__(self, db_collection, db_document, project_id, version_id, ngrok_secret_id):
        self.db_collection = db_collection
        self.db_document = db_document
        self.project_id = project_id
        self.version_id = version_id
        self.ngrok_secret_id = ngrok_secret_id

    def init_webhook(self):
        # Establish connectivity
        listener = ngrok.forward(5000,  # Port to forward
                                domain="native-koi-miserably.ngrok-free.app",  # Domain to use, I.E where we receive the webhook.
                                authtoken = access_secret_version(self.project_id, self.ngrok_secret_id, self.version_id)   # Auth token
                                )
        print(f"NGROK authenticated! \nIngress established at {listener.url()}")

    # Define the webhook endpoint
    async def webhook_update_db(self, payload) -> dict:
        payload = await payload

        database_epic_instance = database_epic(self.db_collection, self.db_document, "", "", "", "")

        if payload.get('action') == 'edited':
            changes = payload.get('changes', {})
            issue = payload.get('issue', {})

            update_data = Task(title=None, comments=None, issueID=None, priority=None, description=None, story_point=None)

            for key in changes.keys():
                print(f"Change detected in: {key}")
                from_value = changes[key].get('from', None)
                print(f"Previous value: {from_value}")
                db_value = getattr(database_epic_instance.tasks, from_value, None)
                new_value = issue.get(key, None)
                if db_value != new_value:
                    if key == 'body':
                        from_value = issue.get('title')
                        parsed_data = parse_body(new_value)
                        for attr, value in parsed_data.items():
                            setattr(update_data, attr, value)
                    else:
                        setattr(update_data, key, new_value)
            
            #Update Firestore
            issue_title = issue.get('title')
            if update_data and issue_title:
                DatabaseManager.update_tasks(self.db_collection, self.db_document, str(from_value), update_data.__dict__)
            
            return {"status": "success", "value updated:": update_data}

        return payload


def parse_body(body: str) -> dict:
    """Parse the body text and extract values for Task attributes."""
    task_data = {
        'description': None,
        'priority': None,
        'story_point': None,
        'comments': None
    }

    body = body.replace('**', '')  # Escape markdown characters
    
    # Regular expressions to extract values
    patterns = {
        'description': r'Description:\s*(.*)',
        'priority': r'Priority:\s*(.*)',
        'story_point': r'Story Point:\s*(\d+)',
        'comments': r'Comments:\s*(.*)'
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, body)
        if match:
            value = match.group(1).strip()
            if key == 'story_point':
                task_data[key] = int(value)  # Convert story_point to int
            else:
                task_data[key] = value
    
    return task_data





