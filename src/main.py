import os
import uvicorn
import httpx
import ngrok
import logging

from fastapi import FastAPI, Request
from contextlib import asynccontextmanager

from database.manager import DatabaseManager
from routers import epics, tasks, users
from Google import sheets
from plugins import PluginManager
from secret_manager import access_secret_version


tags_metadata = [
    {"name": "Users", "description": "Operations pertaining to users. The **login** logic is also here."},
    {"name": "Epics", "description": "Management of epics."},
    {"name": "Tasks", "description": "Management of tasks within epics."}
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize lifespan objects, like httpx client, db, tunneling services, etc. Ensure they are closed on shutdown."""
    app.state.client = httpx.AsyncClient(timeout=120)
    app.state.db = DatabaseManager("epics")
    app.state.logger = logging.getLogger("uvicorn.error")
    app.state.logger.info("Setting up NGROK Tunnel.")
    ngrok.forward(5000, 
                  domain="native-koi-miserably.ngrok-free.app", 
                  authtoken=access_secret_version("trackpointdb", "NGROK_AUTHTOKEN", "latest"))
    app.state.logger.info(f"NGROK authenticated! Ingress established at: https://native-koi-miserably.ngrok-free.app")

    yield
    
    # The Client closes on shutdown
    app.state.logger.info("Closing HTTPX client.")
    await app.state.client.aclose()
    
    app.state.logger.info("Tearing Down Ngrok Tunnel")
    ngrok.disconnect()

# Initialize FastAPI application
app = FastAPI(title="TrackPoint-Backend", 
              description="API for TrackPoint's backend.",
              openapi_tags=tags_metadata,
              lifespan=lifespan)
app.include_router(epics.router)
app.include_router(tasks.router)
app.include_router(users.router)

@app.post("/", tags=["Root"])
async def root(request: Request = None):
    payload = await request.json()
    request.app.state.logger.info(f"Received payload: {payload}")
    plugin = PluginManager(app)
    

    await sheets.handle_sheet_webhook_event(request, plugin)
    
    return {"status": 200, "message": "DB updated Succesfully"}

def main():
    try:
        uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), log_level="info", reload=True)
    except KeyboardInterrupt:
        print("Closing listener")

if __name__ == "__main__":
    main()
    

