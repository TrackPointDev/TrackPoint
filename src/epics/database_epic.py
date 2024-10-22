from epics.base_epic import BaseEpic
from database.manager import DatabaseManager

class database_epic(BaseEpic):
    """
    Epic class representing a database epic. Inherits from BaseEpic.
    """
    def __init__(self, collection, document, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.collection = collection
        self.document = document
        self.start()

    def start(self):
        """
        Method to populate the epic with data from the database. Retrieves fields such as title, value, problem, feature, and tasks.
        If no document is found, raises an exception.
        """
        try:
            DatabaseManager("epics", "MVP for TrackPoint")
            data = DatabaseManager.fetch_database()
            self.title = data.get('title')
            self.value = data.get('value')
            self.problem = data.get('problem')
            self.feature = data.get('feature')
            self.tasks = data.get('tasks', [])
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
        

    def create_issues(self):
        pass

    def get_issues(self):
        pass

    def delete_issue(self, title):
        pass

    def format_body(self, task):
        pass

    def load_json(self, file_path):
        pass

    def save_json(self, file_path):
        pass    