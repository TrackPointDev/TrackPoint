import os.path

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from secret_manager import access_secret_version_json

def initfirebase():
    """Method to initialize the Firebase connection and create a database instance.

    See docs: firebase.google.com/docs/firestore/quickstart"""
    
    """
    # Get the path to the Firebase credentials file
    base_dir = os.path.dirname(__file__)
    cred_path = os.path.join(base_dir, 'firebase_creds.json')
    cred = credentials.Certificate(cred_path)
    """

    # With Google Secret Manager
    project_id = "trackpointdb"
    secret_id = "firebase_creds"
    version_id = "latest"
    cred = credentials.Certificate(access_secret_version_json(project_id, secret_id, version_id))
    
    print(f"cred:", cred)
    firebase_admin.initialize_app(cred)
    db = firestore.client()

    return db

