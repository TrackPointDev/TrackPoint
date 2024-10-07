import ngrok
import time
import os
import json
import uvicorn
from fastapi import FastAPI
from secret_manager import access_secret_version
from fastapi import Request

# Initialize FastAPI application
app = FastAPI()

# Define the webhook endpoint
@app.post("/")
async def read_webhook(request: Request) -> dict:
    payload = await request.json()
    print(json.dumps(payload, indent=4))
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

