import re

from database import initfirebase
from database.models import Epic, Task, User
from typing import Optional, Dict, Any, List, Union
from fastapi import HTTPException
from Google import sheets
from google.cloud.firestore_v1.base_query import FieldFilter


# TODO: fuck doc_ref. Make all endpoints initialize doc_ref based on argument parameter.
# TODO: Refactor DatabaseManager class, such that references are dynamícally passed from function caller.
class DatabaseManager:
    def __init__(self, db_collection, db_document: Optional[str] = None) -> None:
        self.db = initfirebase()
        self.db_collection = db_collection
        self.db_document = db_document
        self.doc_ref = self.db.collection(self.db_collection).document(self.db_document) if db_document else None


    def add_task(self, task: Task, epic_id: str) -> None:
        """
        Adds a new task to the 'tasks' list within the Firestore document.
        Args:
            task (dict): The task data to be added.
        Returns:
            None
        """
        print(f"lll {epic_id}")
        try:
            doc_ref = self.db.collection(self.db_collection).document(epic_id)
            doc = doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                tasks = data.get('tasks', [])
                tasks.append(task.model_dump(mode='json'))
                doc_ref.update({'tasks': tasks})
                print(f"Task added successfully to document '{epic_id}' in collection '{self.db_collection}'!")
            else:
                raise Exception(f"No such document '{self.db_document}' in collection '{self.db_collection}'")
        except Exception as e:
            raise Exception(e)
        
    def update_task(self, task: Task, epic_id: str) -> None:
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
            doc_ref = self.db.collection(self.db_collection).document(epic_id)
            doc = doc_ref.get()

            if doc.exists:
                data = doc.to_dict()
                tasks = data.get('tasks', [])
    
                task_found = False

                for item in tasks:
                    if (task.taskID is not None and item.get("issueID") == task.taskID):
                        item.update(task.model_dump(mode='json'))
                        task_found = True
                        break

                if not task_found:
                    print(f"Task with title: '{task.title}' not found.")
                    return None
                
                self.doc_ref.update({'tasks': tasks})
                print(f"Task '{task.title}' updated successfully!")
            else:
                raise Exception(f"No such document '{self.db_document}' in collection '{self.db_collection}'")
        except Exception as e:
            raise Exception(f"Error with writing to Google Cloud: {e}")
        
    def get_task(self, task_identifier: Union[int, str], epic_id: str ):
        """
        Fetch specific task from Firestore document based on the task_identifier. Or return all tasks if no identifier is provided.

        Args:
            task_identifier (Union[int, str]): The unique identifier of the task, either an integer (issueID) or a string (task_title).
            epic_id (str): The title of the epic. 
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
            doc_ref = self.db.collection(self.db_collection).document(epic_id)
            doc = doc_ref.get()

            if doc.exists:
                data = doc.to_dict()
                tasks = data['tasks']
                for task in tasks:
                    if (isinstance(task_identifier, int) and task['taskID'] == task_identifier) or \
                       (isinstance(task_identifier, str) and task['title'] == task_identifier):
                        print(f"Task with identifier '{task_identifier}' found in document '{epic_id}' in collection '{self.db_collection}'!")
                        found_task = Task(**task)
                        return found_task.model_dump(mode='json')
                return {"status": 404, "message": f"No task with identifier '{task_identifier}' found in document '{epic_id}' in collection '{self.db_collection}'"}
            else:
                raise Exception(f"No such document '{epic_id}' in collection '{self.db_collection}'")
        except Exception as e:  # Catch any exceptions
            print(f"An error occurred: {e}")
            return None
        
    def get_tasks_list(self, epic_id: str) -> List:
        """
        Retrieves entire list of 'tasks' from the Firestore document.
        Args:
            task (dict): The task data to be added.
        Returns:
            None
        """
        try:
            print(f"Retrieving task list from document '{epic_id}' in collection '{self.db_collection}'...")
            doc_ref = self.db.collection(self.db_collection).document(epic_id)
            doc = doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                tasks = data.get('tasks', [])
                print(f"Successfully retreived task list from document '{epic_id}' in collection '{self.db_collection}'!")
                return tasks
            else:
                raise Exception(f"No such document '{epic_id}' in collection '{self.db_collection}'")
        except Exception as e:
            raise Exception(e)
        
    def delete_task(self, task: Task, epic_id: str) -> None:
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

        print(f"Deleting task with title: '{task.title}' from document '{epic_id}' in collection '{self.db_collection}'...")

        doc_ref = self.db.collection(self.db_collection).document(epic_id)
        try:
            doc = doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                tasks = data.get('tasks', [])

                updated_tasks = []
                for t in tasks:
                    # t is a dict from Firestore, task is a Task model
                    if (isinstance(task.issueID, int) and t.get('issueID') == task.issueID) \
                            or (isinstance(task.title, str) and t.get('title') == task.title):
                        # Skip to "delete" task
                        continue
                    updated_tasks.append(t)

                doc_ref.update({'tasks': updated_tasks})
                print(f"Task with identifier '{task.title}' deleted successfully from document '{self.db_document}' in collection '{epic_id}'!")
            else:
                raise Exception(f"No such document '{self.db_document}' in collection '{epic_id}'")
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
        
    def get_epic(self, epic_title: str = None, identifier: str = None) -> Epic:
        """Retreive an epic from the Firestore database based on the epic_title or identifier."""
        try:
            if epic_title:
                doc_ref = self.db.collection(self.db_collection).document(epic_title)
                doc = doc_ref.get()
                if doc.exists:
                    doc = doc.to_dict()
                    return Epic(**doc)
                else:
                    print(f"No such document '{epic_title}' in collection '{self.db_collection}'")
                    return None
            elif identifier:
                query = (
                    self.db.collection(self.db_collection)
                    .where(filter=FieldFilter("repoName", "==", identifier))
                    .limit(1))
                docs = query.stream()
                for doc in docs:
                    if doc.exists:
                        doc = doc.to_dict()
                        return Epic(**doc)
                print(f"No document with repoName '{identifier}' found in collection '{self.db_collection}'")
                return None
            else:
                raise ValueError("Either epic_title or identifier must be provided.")
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
            self.db.collection(self.db_collection).document(epic_title).update(epic_data)
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
                if task_object != None:
                    task_list.append(task_object)
            epic_data.tasks = task_list

        user = User(
            name=payload.get("user").get("nickname"),
            email=payload.get("user").get("email"),
            epics=[epic_data.title]
        )

        epic_data.users.append(user) 

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
            name=user_data.get("nickname", "Anonymous"),
            email=user_data.get("email", None),
            role=user_data.get("role", None),
            uID=user_data.get("uID", "")
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
        
    @staticmethod
    def parse_body(body: str) -> dict:
        """Parse the body text and extract values for Task attributes."""
        task_data = {
            'description': None,
            'priority': None,
            'story_point': None,
            'comments': None
        }
        body = body.replace('**', '')  # Escape markdown characters
        
        # Regular expressions to extract values
        patterns = {
            'description': r'Description:\s*(.*)',
            'priority': r'Priority:\s*(.*)',
            'story_point': r'Story Point:\s*(\d+)',
            'comments': r'Comments:\s*(.*)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, body)
            if match:
                value = match.group(1).strip()
                if key == 'story_point':
                    task_data[key] = int(value)  # Convert story_point to int
                else:
                    task_data[key] = value
        
        return task_data