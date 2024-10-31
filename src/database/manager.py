from database import initfirebase
from database.models import Task
from typing import Optional, Dict, Any, List, Union

#Maybe more of a document manager than a database manager but I'm not sure what to call it
class DatabaseManager:
    def __init__(self, db_collection, db_document) -> None:
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

    def update_db(self, updates):
        try:
            self.doc_ref.update(updates)
            print(f"Document '{self.db_document}' in collection '{self.db_collection}' updated successfully!")
        except Exception as e:  # Catch any exceptions
            print(f"An error occurred: {e}")
    
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
            print(f"Document '{self.db_document}' in collection '{self.db_collection}' added successfully!")
        except Exception as e:  # Catch any exceptions
            print(f"An error occurred: {e}")
            return None

    def delete_epic(self) -> None:
        try:
            self.doc_ref.delete()
            print(f"Document '{self.db_document}' in collection '{self.db_collection}' deleted successfully!")
        except Exception as e:  # Catch any exceptions
            print(f"An error occurred: {e}")
            return None
    
    def update_task(self, task_identifier, updated_task):
        """
        Updates a specific task in the 'tasks' list within a Firestore document.
        Args:
            db_collection (str): The name of the Firestore collection.
            db_document (str): The name of the document within the collection.
            task_identifier (str): The title of the task to be updated.
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
