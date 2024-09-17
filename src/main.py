from googleapiclient.errors import HttpError

import json
import dataclasses

from src.Google import sheets
from src.database import initfirebase
from src.github import create_github_issue

cache = {}


# Define a custom JSON encoder to handle dataclasses. Mostly just here so I could print the dataclasses as JSON
# in the terminal.
class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


spreadsheet_id = "1iC75ObLb5ZvJ4NedUmnA5O98XGVNYno0IeJYFg2DVZ8"     # ID of the current spreadsheet.


def main():
    try:
        # Retrieve data from 'Epic' and 'Tasks' sheets.
        epic_sheet = sheets.get_sheet("Epic", spreadsheet_id)
        tasks_sheet = sheets.get_sheet("Tasks", spreadsheet_id)

        task_list = []

        # Transform the data from the 'Epic' sheet into an 'Epic' object.
        epic_data = sheets.transform_to_epics(epic_sheet)

        # Transform the data from the 'Tasks' sheet into a list of 'Task' objects.
        if epic_data:
            for task in tasks_sheet:
                task_object = task.to_task()
                task_list.append(task_object.__dict__)
            epic_data.tasks = task_list

        # Convert the 'Epic' and 'Tasks' objects into JSON format and print them. Purely for debugging purposes.
        epic_json = json.dumps(epic_data, cls=EnhancedJSONEncoder, indent=4)
        task_json = json.dumps(task_list, cls=EnhancedJSONEncoder, indent=4)
        print(epic_json)
        print(task_json)

        # Draft a request to create a new issue on GitHub. This is only a test. Ideally we should iterate over each task
        # and create a new issue for each one.
        request_data = {
            "title": epic_data.title,
            "body": epic_data.problem + "\n" + epic_data.feature + "\n" + epic_data.value,
        }

        create_github_issue(data=request_data)

        # Initialize the Firestore database and add the 'Epic' object to the database along with its tasks.
        db = initfirebase()

        doc_ref = db.collection("epics").document(epic_data.title)
        doc_ref.set({"title": epic_data.title,
                     "problem": epic_data.problem,
                     "feature": epic_data.feature,
                     "value": epic_data.value,
                     "tasks": task_list})
        print("Document successfully added to Firestore")

    except HttpError as err:
        print(err)


if __name__ == "__main__":
    main()
