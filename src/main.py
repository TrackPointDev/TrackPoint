import os
import uvicorn
import asyncio
import httpx
from fastapi import FastAPI
from fastapi import Request
from contextlib import asynccontextmanager

from database.manager import DatabaseManager
from database.models import Epic
from routers import epics, tasks, users
from Google import sheets
from plugins import PluginManager

from webhook import Webhook

tags_metadata = [
    {"name": "Users", "description": "Operations pertaining to users. The **login** logic is also here."},
    {"name": "Epics", "description": "Management of epics."},
    {"name": "Tasks", "description": "Management of tasks within epics."}
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and close the httpx client on startup and shutdown."""
    app.state.client = httpx.AsyncClient(timeout=120)
    app.state.db = DatabaseManager("epics")
    yield
    # The Client closes on shutdown
    await app.state.client.aclose()

# Initialize FastAPI application
app = FastAPI(title="TrackPoint-Backend", 
              description="API for TrackPoint's backend.",
              openapi_tags=tags_metadata,
              lifespan=lifespan)
app.include_router(epics.router)
app.include_router(tasks.router)
app.include_router(users.router) 

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


@app.post("/")
async def root(request: Request = None):
    payload = await request.json()
    print(f"Received payload: {payload}")

    plugin = PluginManager(app)

    await sheets.handle_sheet_webhook_event(request, plugin)
    
    return {"status": 200, "message": "DB updated Succesfully"}

def main():
    try:
        uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    except KeyboardInterrupt:
        print("Closing listener")

if __name__ == "__main__":
    main()
    

