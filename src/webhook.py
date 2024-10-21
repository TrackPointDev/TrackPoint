import ngrok
import time
import re
import os
import json
import uvicorn
from fastapi import FastAPI

from database_epic import database_epic
from secret_manager import access_secret_version
from database.manager import update_db, update_tasks
from fastapi import Request

db_collection = "epics"
db_document = "MVP for TrackPoint"

# Initialize FastAPI application
app = FastAPI()

# Define the webhook endpoint
@app.post("/")
async def read_webhook(request: Request) -> dict:
    payload = await request.json()
    print(json.dumps(payload, indent=4))

    database_epic_instance = database_epic(db_collection, db_document, "", "", "", "")
    print(json.dumps(database_epic_instance.tasks, indent=4))

    if payload.get('action') == 'edited':
        changes = payload.get('changes', {})
        issue = payload.get('issue', {})

        update_data = {}
        for key in changes.keys():
            print(f"Change detected in: {key}")
            from_value = changes[key].get('from', None)
            print(f"Previous value: {from_value}")
            db_value =  getattr(database_epic_instance.tasks, from_value, None)
            new_value = issue.get(key, None)
            if db_value != new_value:
                update_data[key] = new_value 
        
        #Update Firestore
        issue_title = issue.get('title')
        if update_data and issue_title:
            print(f"Updating with title: {db_value}")
            update_tasks(db_collection, db_document, str(from_value), update_data)
        
        return {"status": "success", "value updated:": update_data}

    return payload

def init_webhook():
    project_id = "trackpointdb" 
    secret_id = "NGROK_AUTHTOKEN"  
    version_id = "latest"  

    # Establish connectivity
    listener = ngrok.forward(5000,  # Port to forward
                            domain="native-koi-miserably.ngrok-free.app",  # Domain to use, I.E where we receive the webhook.
                            authtoken = access_secret_version(project_id, secret_id, version_id)   # Auth token
                            )
    print(f"NGROK authenticated! \nIngress established at {listener.url()}")

    # Keep the listener alive
    try:
        uvicorn.run(app, host="0.0.0.0", port=5000)
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Closing listener")

init_webhook()

