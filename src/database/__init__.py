import os.path

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from secret_manager import access_secret_version_json

def initfirebase():
    """Method to initialize the Firebase connection and create a database instance.

    See docs: firebase.google.com/docs/firestore/quickstart"""

    # With Google Secret Manager
    project_id = "trackpointdb"
    secret_id = "firebase_creds"
    version_id = "latest"
    cred = credentials.Certificate(access_secret_version_json(project_id, secret_id, version_id))
    
    try:
        # Try to get the default app
        app = firebase_admin.get_app()
    except ValueError:
        # If the app does not exist, initialize it
        app = firebase_admin.initialize_app(cred)

    # Initialize Firestore client
    db = firestore.client(app=app)

    return db

