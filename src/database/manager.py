import json
from database import initfirebase

class DatabaseManager:
    def __init__(self) -> None:
        self.db = initfirebase()
        
    def fetch_database(self, db_collection, db_document):
        try:
            doc_ref = self.db.collection(db_collection).document(db_document)
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

    def update_db(self, db_collection, db_document, updates):
        try:
            doc_ref = self.db.collection(db_collection).document(db_document)
            doc_ref.update(updates)
            print(f"Document {db_document} in collection {db_collection} updated successfully!")
        except Exception as e:  # Catch any exceptions
            print(f"An error occurred: {e}")
            return None

    def add_to_db(self, db_collection, db_document, epic_data, data):
        try:
            doc_ref = self.db.collection(db_collection).document(db_document)
            doc_ref.set({
                "title": epic_data.title,
                "problem": epic_data.problem,
                "feature": epic_data.feature,
                "value": epic_data.value,
                "tasks": data
            })
            print(f"Document {db_document} in collection {db_collection} added successfully!")
        except Exception as e:  # Catch any exceptions
            print(f"An error occurred: {e}")
            return None
        
    def delete_epic(self, db_collection, db_document):
        try:
            doc_ref = self.db.collection(db_collection).document(db_document)
            doc_ref.delete()
            print(f"Document {db_document} in collection {db_collection} deleted successfully!")
        except Exception as e:  # Catch any exceptions
            print(f"An error occurred: {e}")
            return None