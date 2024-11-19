import os
import uvicorn
from fastapi import FastAPI
from fastapi import Request

from database.manager import DatabaseManager
from database.setup import setup_database
from webhook import Webhook
from routers import epics, tasks


tags_metadata = [
    {"name": "Users", "description": "Operations pertaining to users. The **login** logic is also here."},
    {"name": "Epics", "description": "Management of epics."},
    {"name": "Tasks", "description": "Management of tasks within epics."}
]


# Initialize FastAPI application
app = FastAPI(title="TrackPoint-Backend", 
              description="API for TrackPoint's backend.",
              openapi_tags=tags_metadata)
app.include_router(epics.router)
app.include_router(tasks.router)


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

config = Config()
initialize_webhook()
db = DatabaseManager(config.db_collection, config.db_document)


@app.post("/")
async def listener(request: Request = None):
    payload = await request.json()
    print(f"Received payload: {payload}")

    return {"status": 200, "message": "Webhook event processed successfully."}


def main():
    try:
        uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
        setup_database(config.spreadsheet_id, db)
    except KeyboardInterrupt:
        print("Closing listener")


if __name__ == "__main__":
    main()
    

