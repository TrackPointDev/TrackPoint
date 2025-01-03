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

from webhook import Webhook

tags_metadata = [
    {"name": "Users", "description": "Operations pertaining to users. The **login** logic is also here."},
    {"name": "Epics", "description": "Management of epics."},
    {"name": "Tasks", "description": "Management of tasks within epics."}
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the Client on startup and add it to the state
    async with httpx.AsyncClient() as client:
        yield {'client': client}
        # The Client closes on shutdown

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

    db = DatabaseManager(config.db_collection)

    async def handle_epic():
        sheet_epic = db.parse_sheet(payload)
        existing_epic = db.get_epic(sheet_epic.title)
        if existing_epic is None:
            db.create_epic(sheet_epic.model_dump(mode='json'))
        else:
            db.update_epic(sheet_epic.title, sheet_epic.model_dump(mode='json'))
        await gh_epic_setup(sheet_epic)

    async def handle_user():
        user = payload.get("user")
        print(f"User: {user}")

        if user["nickname"] and user["email"] is not None:
            existing_user = db.get_all_users(user["nickname"])
            if existing_user is None:
                db.create_user(user)
                print(f"Created new user: {user["nickname"]}")
            else:
                print(f"User {user["nickname"]} already exists")
        else:
            return {"status": 400, "message": "User has no nickname or email"}
    
    # Run both functions concurrently. Check for epics and users.
    await asyncio.gather(handle_epic(), handle_user())
    return {"status": 200, "message": "DB updated Succesfully"}

async def gh_epic_setup(epic: Epic):
    """
    Endpoint to handle GitHub webhooks.
    """
    epic_data = epic.model_dump(mode='json')
    print(f"Received Epic: {epic_data}")
    url = "https://trackpoint-github-gcf-87527377987.europe-west3.run.app/epic/setup"

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=epic_data)
        response.raise_for_status()  # throw an error if not 2xx
        return response.json()

    LOGGER.info("Received GitHub webhook.")
    return {"status": 200, "message": "Received GitHub webhook."}

def main():
    try:
        uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    except KeyboardInterrupt:
        print("Closing listener")

if __name__ == "__main__":
    main()
    

