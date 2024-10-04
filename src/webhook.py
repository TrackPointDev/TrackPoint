import ngrok
import time
import os
import json

from secret_manager import access_secret_version

project_id = "trackpointdb"  # Replace with your GCP project ID
secret_id = "NGROK_AUTHTOKEN"  # Replace with your secret ID in Google Cloud
version_id = "latest"  # Replace with the version number or use "latest"

# Retrieve the secret value and set it as an environment variable.
os.environ["NGROK_AUTHTOKEN"] = access_secret_version(project_id, secret_id, version_id)
print("NGROK_AUTHTOKEN has been set.")

# Establish connectivity
listener = ngrok.forward(5000, authtoken_from_env=True)
print(f"Ingress established at {listener.url()}")

# Keep the listener alive
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Closing listener")


