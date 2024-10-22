from database import initfirebase
from typing import Optional, Dict, Any

#Maybe more of a document manager than a database manager but I'm not sure what to call it
class DatabaseManager:
    def __init__(self, db_collection, db_document) -> None:
        self.db = initfirebase()
        self.db_collection = db_collection
        self.db_document = db_document
        self.doc_ref = self.db.collection(self.db_collection).document(self.db_document)
        
    def fetch_database(self):
        try:
            doc = self.doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                return data
                #return json.dumps(data, indent=4)
            else:
                print(f"No such document {self.db_document} in collection {self.db_collection}")
                return None
        except Exception as e:  # Catch any exceptions
            print(f"An error occurred: {e}")
            return None

    def update_db(self, updates):
        try:
            self.doc_ref.update(updates)
            print(f"Document {self.db_document} in collection {self.db_collection} updated successfully!")
        except Exception as e:  # Catch any exceptions
            print(f"An error occurred: {e}")

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
        else:
            print(f"No such document {db_document} in collection {db_collection}")
            return None
    except Exception as e:  # Catch any exceptions
            print(f"An error occurred: {e}")
            return None
    

    # Should match the format of a base epic object
    def add_to_db(self, epic_data, data):
        try:
            self.doc_ref.set({
                "title": epic_data.title,
                "problem": epic_data.problem,
                "feature": epic_data.feature,
                "value": epic_data.value,
                "tasks": data
            })
            print(f"Document {self.db_document} in collection {self.db_collection} added successfully!")
        except Exception as e:  # Catch any exceptions
            print(f"An error occurred: {e}")
            return None
    
    def get_task_with_id(self, task_id: int) -> Optional[Dict[str, Any]]:
        if not isinstance(task_id, int):
            raise ValueError("task_id must be an integer")
        
        try:
            doc = self.doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                tasks = data['tasks']
                for task in tasks:
                    if task['issueID'] == task_id:
                        return task
                return None
            else:
                print(f"No such document {self.db_document} in collection {self.db_collection}")
                return None
        except Exception as e:  # Catch any exceptions
            print(f"An error occurred: {e}")
            return None
    
    def get_task_with_title(self, task_title: str) -> Optional[Dict[str, Any]]:
        if not isinstance(task_title, str):
            raise ValueError("task_title must be a string")
    
        try:
            doc = self.doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                tasks = data['tasks']
                for task in tasks:
                    if task['title'] == task_title:
                        return task
                return None
            else:
                print(f"No such document {self.db_document} in collection {self.db_collection}")
                return None
        except Exception as e:  # Catch any exceptions
            print(f"An error occurred: {e}")
            return None

    def delete_epic(self) -> None:
        try:
            self.doc_ref.delete()
            print(f"Document {self.db_document} in collection {self.db_collection} deleted successfully!")
        except Exception as e:  # Catch any exceptions
            print(f"An error occurred: {e}")
            return None
    
    def update_tasks(db_collection, db_document, task_title, updated_task):
    """
    Updates a specific task in the 'tasks' list within a Firestore document.
    Args:
        db_collection (str): The name of the Firestore collection.
        db_document (str): The name of the document within the collection.
        task_title (str): The title of the task to be updated.
        updated_task (dict): The updated task data.
    Returns:
        None
    Raises:
        Exception: If an error occurs during the update operation, it will be caught and printed.
    """
    db = initfirebase()
    try:
        doc_ref = db.collection(db_collection).document(db_document)
        doc = doc_ref.get()
        
        if doc.exists:
            data = doc.to_dict()
            tasks = data.get('tasks', [])
            
            task_found = False
            for task in tasks:
                if task.get('title') == task_title:
                    task.update({k: v for k, v in updated_task.items() if v is not None})
                    task_found = True
                    break
            
            if not task_found:
                print(f"Task with title: '{task_title}' not found.")
                return None
            
            doc_ref.update({'tasks': tasks})
            print(f"Task {task_title} updated successfully!")
        else:
            print(f"No such document {db_document} in collection {db_collection}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
