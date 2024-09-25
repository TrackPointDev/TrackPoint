import json
from database import initfirebase

def fetch_database(db_collection, db_document):
    db = initfirebase()
    # fetch data using the db instance
    data = db.collection(db_collection).document(db_document).get().to_dict()

    json_data = json.dumps(data, indent=4)

    return json_data