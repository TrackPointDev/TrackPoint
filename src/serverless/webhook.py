import asyncio
import json
import time
import uvicorn
import os

from fastapi import FastAPI, Request


app = FastAPI(title="TrackPointWebhook")

@app.post("/webhook")
def webhook():
    return {"message": "Hello World!"}
