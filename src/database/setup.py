    
import json
import dataclasses
from googleapiclient.errors import HttpError
from Google import sheets

# Define a custom JSON encoder to handle dataclasses. Mostly just here so I could print the dataclasses as JSON
# in the terminal
class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)

def setup_database(spreadsheet_id, db_manager):
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
                if task_object.title != None:
                    task_list.append(task_object.__dict__)
            epic_data.tasks = task_list

        # Convert the 'Epic' and 'Tasks' objects into JSON format and print them. Purely for debugging purposes.
        epic_json = json.dumps(epic_data, cls=EnhancedJSONEncoder, indent=4)
        task_json = json.dumps(task_list, cls=EnhancedJSONEncoder, indent=4)
        print(epic_json)
        print(task_json)
        
        db_manager.add_to_db(epic_data, task_list)

    except HttpError as err:
        print(err)