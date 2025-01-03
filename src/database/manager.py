from database import initfirebase
from database.models import Epic, Task, User
from typing import Optional, Dict, Any, List, Union
from fastapi import HTTPException
from Google import sheets
from google.cloud.firestore_v1.base_query import FieldFilter

from firebase_functions.firestore_fn import (
  on_document_created,
  on_document_deleted,
  on_document_updated,
  on_document_written,
  Event,
  Change,
  DocumentSnapshot,
)

#Maybe more of a document manager than a database manager but I'm not sure what to call it
class DatabaseManager:
    def __init__(self, db_collection, db_document: Optional[str] = None) -> None:
        self.db = initfirebase()
        self.db_collection = db_collection
        self.db_document = db_document
        self.doc_ref = self.db.collection(self.db_collection).document(self.db_document)
        
    def fetch_database(self):
        """
        Fetches a document from a specified Firestore collection.
        Returns:
            dict: The document data as a dictionary if the document exists.
            None: If the document does not exist or an error occurs.
        """
        try:
            doc = self.doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                return data
                #return json.dumps(data, indent=4)
            else:
                print(f"No such document '{self.db_document}' in collection '{self.db_collection}'")
                return None
        except Exception as e:  # Catch any exceptions
            print(f"An error occurred: {e}")
            return None
    
    @on_document_updated(document="epics/MVP for TrackPoint")
    def db_event_listener(self, event: Event[Change[DocumentSnapshot]]) -> None:
        print(f"Change detected on document {event.params['title']}")

        change = event.data
        if change.before.exists:
            before_data = change.before.to_dict()
        else:
            before_data = {}

        if change.after.exists:
            after_data = change.after.to_dict()
        else:
            after_data = {}

        changed_fields = {k: after_data[k] for k in after_data if before_data.get(k) != after_data.get(k)}

        print(f"Changed fields: {changed_fields}")
        return changed_fields


    def add_task(self, task: Dict[str, Any]) -> None:
        """
        Adds a new task to the 'tasks' list within the Firestore document.
        Args:
            task (dict): The task data to be added.
        Returns:
            None
        """
        try:
            doc = self.doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                tasks = data.get('tasks', [])
                tasks.append(task)
                self.doc_ref.update({'tasks': tasks})
                print(f"Task added successfully to document '{self.db_document}' in collection '{self.db_collection}'!")
            else:
                raise Exception(f"No such document '{self.db_document}' in collection '{self.db_collection}'")
        except Exception as e:
            raise Exception(e)
        
    def update_task(self, task_identifier, updated_task):
        """
        Updates a specific task in the 'tasks' list within a Firestore document.
        Args:
            task_identifier (int or str): The title/ID of the task to be updated.
            updated_task (dict): The updated task data.
        Returns:
            None
        Raises:
            Exception: If an error occurs during the update operation, it will be caught and printed.
        """
        try:
            doc = self.doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                tasks = data.get('tasks', [])
                
                task_found = False

                for task in tasks:
                    if (isinstance(task_identifier, int) and task.get('issueID') == task_identifier) or \
                        (isinstance(task_identifier, str) and task.get('title') == task_identifier):
                        task.update({k: v for k, v in updated_task.items() if v is not None})
                        task_found = True
                        break
                
                if not task_found:
                    print(f"Task with title: '{task_identifier}' not found.")
                    return None
                
                self.doc_ref.update({'tasks': tasks})
                print(f"Task '{task_identifier}' updated successfully!")
            else:
                raise Exception("No such document '{self.db_document}' in collection '{self.db_collection}'")
        except Exception as e:
            raise Exception(f"Error with writing to Google Cloud: {e}")
        
    def get_task(self, task_identifier: Union[int, str]) -> Optional[Dict[str, Any]]:
        """
        Fetch specific task from Firestore document based on the task_identifier.

        Args:
            task_identifier (Union[int, str]): The unique identifier of the task, either an integer (task_id) or a string (task_title).
        Returns:
            dict: The task data as a dictionary if the task exists.
            None: If the task does not exist or an error occurs.
        Raises:
            ValueError: If task_identifier is neither an integer nor a string.
            Exception: If an error occurs during the fetch operation, it will be caught and printed.
        """
        if not isinstance(task_identifier, (int, str)):
            raise ValueError("task_identifier must be an integer or a string")
        
        try:
            doc = self.doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                tasks = data['tasks']
                for task in tasks:
                    if (isinstance(task_identifier, int) and task['issueID'] == task_identifier) or \
                       (isinstance(task_identifier, str) and task['title'] == task_identifier):
                        return task
                return None
            else:
                raise Exception(f"No such document '{self.db_document}' in collection '{self.db_collection}'")
        except Exception as e:  # Catch any exceptions
            print(f"An error occurred: {e}")
            return None
        
    def get_tasks_list(self) -> List:
        """
        Retrieves entire list of 'tasks' from the Firestore document.
        Args:
            task (dict): The task data to be added.
        Returns:
            None
        """
        try:
            doc = self.doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                tasks = data.get('tasks', [])
                print(f"Successfully retreived task list from document '{self.db_document}' in collection '{self.db_collection}'!")
                return tasks
            else:
                raise Exception(f"No such document '{self.db_document}' in collection '{self.db_collection}'")
        except Exception as e:
            raise Exception(e)
        
    def delete_task(self, task_identifier: Union[int, str]) -> None:
        """
        Deletes a specific task from the 'tasks' list within the Firestore document.
        Args:
            task_identifier (Union[int, str]): The unique identifier of the task, either an integer (task_id) or a string (task_title).
        Returns:
            None
        Raises:
            ValueError: If task_identifier is neither an integer nor a string.
            Exception: If an error occurs during the delete operation, it will be caught and printed.
        """
        if not isinstance(task_identifier, (int, str)):
            raise ValueError("task_identifier must be an integer or a string")
        
        try:
            doc = self.doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                tasks = data.get('tasks', [])
                tasks = [task for task in tasks if not ((isinstance(task_identifier, int) and task['issueID'] == task_identifier) or 
                                                        (isinstance(task_identifier, str) and task['title'] == task_identifier))]
                self.doc_ref.update({'tasks': tasks})
                print(f"Task with identifier '{task_identifier}' deleted successfully from document '{self.db_document}' in collection '{self.db_collection}'!")
            else:
                raise Exception(f"No such document '{self.db_document}' in collection '{self.db_collection}'")
        except Exception as e:
            print(f"An error occurred: {e}")
    
    def create_epic(self, epic: dict) -> None:
        try:
            self.db.collection(self.db_collection).document(epic["title"]).set(epic)
            print(f"Document '{epic["title"]}' in collection '{self.db_collection}' added successfully!")
        except Exception as e:  
            raise Exception(e)

    def delete_epic(self, epic_title) -> None:
        try:
            docs = self.db.collection(self.db_collection).stream()

            for doc in docs:
                if doc.id == epic_title:
                    doc.reference.delete()
                    print(f"Document '{epic_title}' in collection '{self.db_collection}' deleted successfully!")
            raise HTTPException(404, 
                                f"No such document '{epic_title}' in collection '{self.db_collection}'")
        except Exception as e:  
            raise Exception(e)
        
    def get_epic(self, epic_title):
        try:
            doc_ref = self.db.collection(self.db_collection).document(epic_title)

            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            else:
                print(f"No such document '{epic_title}' in collection '{self.db_collection}'")
                return None
        except Exception as e:  
            raise Exception(e)
    
    def get_all_epics(self) -> List:
        try:
            docs = self.db.collection(self.db_collection).stream()
            epics = []
            for doc in docs:
                epics.append(doc.id)
            return epics
        except Exception as e:  
            raise Exception(e)
        
    def update_epic(self, epic_title, epic_data):
        try:
            self.db.collection(self.db_collection).document(epic_title).set(epic_data)
            print(f"Document '{epic_title}' in collection '{self.db_collection}' updated successfully!")
        except Exception as e:  
            raise Exception(e)
    
    def parse_sheet(self, payload: dict) -> Epic:
        """
        Parses a Google Sheet into an Epic object.
        Args:
            sheet (dict): The Google Sheet data to be parsed.
        Returns:
            Epic: The parsed Epic object.
        """

        # Retrieve data from 'Epic' and 'Tasks' sheets respectively.
        epic_sheet = sheets.get_sheet("Epic", payload.get("spreadsheetId"))
        tasks_sheet = sheets.get_sheet("Tasks", payload.get("spreadsheetId"))

        task_list = []

        # Transform the data from the 'Epic' sheet into an 'Epic' object.
        epic_data = sheets.transform_to_epics(epic_sheet, payload)
        
        # Transform the data from the 'Tasks' sheet into a list of 'Task' objects.
        if epic_data:
            for task in tasks_sheet:
                task_object = task.to_task()
                if task_object.title != None:
                    task_list.append(task_object)
            epic_data.tasks = task_list

        user = User(
            name=payload.get("user").get("nickname"),
            email=payload.get("user").get("email"),
            epics=[epic_data.title]
        )

        epic_data.users.append(user) 

        # Convert the 'Epic' and 'Tasks' objects into JSON format and print them. Purely for debugging purposes.
        #print(epic_data.model_dump(mode='json'))

        return epic_data
    
    def parse_user(self, payload: dict) -> User:
        """
        Parses a user from a payload.
        Args:
            payload (dict): The payload data to be parsed.
        Returns:
            User: The parsed User object.
        """
        user_data = payload.get("user")
        user = User(
            name=user_data.get("nickname"),
            email=user_data.get("email"),
            role=user_data.get("role"),
            uID=user_data.get("uID")
        )
        return user

    
    def create_user(self, payload: dict) -> None:
        try:
            user = self.parse_user(payload)
            doc_ref = self.db.collection("users").document()
            doc_ref.set(user.model_dump(mode='json'))
            print(f"Document '{user.name}' in collection 'users' added successfully!"
                  f"\nUser ID: '{doc_ref.id}'")
            user.uID = doc_ref.id
            doc_ref.set(user.model_dump(mode='json'))
        except Exception as e:  
            raise Exception(e)
        
    def get_user(self, user_name):
        try:
            doc_ref = self.db.collection("users").where("name", "==", user_name)

            doc = doc_ref.get()
            if doc is not None:
                return doc.to_dict()
            else:
                print(f"No such document '{user_name}' in collection '{self.db_collection}'")
                return None
        except Exception as e:  
            raise Exception(e)

    def get_all_users(self, user: Optional[str] = None):
        try:
            if user is None:
                docs = self.db.collection("users").stream()
                users = []
                for doc in docs:
                    users.append(doc.id)
                return users
            else:
                query = (self.db.collection("users").where(filter=FieldFilter("name", "==", user))).stream()
                for doc in query:
                    user_data = doc.to_dict()
                    user_data['id'] = doc.id
                    return user_data
        except Exception as e:  
            raise Exception(e)