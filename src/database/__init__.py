import os.path

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


def initfirebase():
    # Use a service account.
    base_dir = os.path.dirname(__file__)
    cred_path = os.path.join(base_dir, 'firebase_creds.json')
    cred = credentials.Certificate(cred_path)

    firebase_admin.initialize_app(cred)

    db = firestore.client()

    return db

