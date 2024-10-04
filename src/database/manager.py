import json
from database import initfirebase

def fetch_database(db_collection, db_document):
    """
    Fetches a document from a specified Firestore collection.
    Args:
        db_collection (str): The name of the Firestore collection.
        db_document (str): The name of the document within the collection.
    Returns:
        dict: The document data as a dictionary if the document exists.
        None: If the document does not exist or an error occurs.
    Raises:
        Exception: If an error occurs during the fetch operation, it will be caught and printed.
    """

    db = initfirebase()
    try:
        doc_ref = db.collection(db_collection).document(db_document)
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            return data
            #return json.dumps(data, indent=4)
        else:
            print(f"No such document {db_document} in collection {db_collection}")
            return None
    except Exception as e:  # Catch any exceptions
        print(f"An error occurred: {e}")
        return None

def update_db(db_collection, db_document, updates):
    db = initfirebase()
    try:
        doc_ref = db.collection(db_collection).document(db_document)
        doc_ref.update(updates)
        print(f"Document {db_document} in collection {db_collection} updated successfully!")
    except Exception as e:  # Catch any exceptions
        print(f"An error occurred: {e}")
        return None
