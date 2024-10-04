from google.cloud import secretmanager
import os
import json

# gcloud init
# gcloud auth application-default login

def access_secret_version(project_id, secret_id, version_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(name=name)
    secret_value = response.payload.data.decode('UTF-8')
    return secret_value

def access_secret_version_json(project_id, secret_id, version_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(name=name)
    secret_value = response.payload.data.decode('UTF-8')
    json_data = json.loads(secret_value)
    return json_data

def set_env_var_from_secret():
    project_id = "trackpointdb"  # Replace with your GCP project ID
    secret_id = "NGROK_AUTHTOKEN"  # Replace with your secret ID in Google Cloud
    version_id = "latest"  # Replace with the version number or use "latest"
    
    # Get the secret value
    authtoken = access_secret_version_json(project_id, secret_id, version_id)
    
    # Set the environment variable
    os.environ["NGROK_AUTHTOKEN"] = authtoken
    print(f"NGROK_AUTHTOKEN has been set.")