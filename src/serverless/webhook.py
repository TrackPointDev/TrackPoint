import asyncio
import json
import time
import uvicorn
import os

from fastapi import FastAPI, Request


app = FastAPI(title="TrackPointWebhook")

@app.post("/webhook")
def webhook(request: Request):
    request = request.json()
    print(request)
    return request
