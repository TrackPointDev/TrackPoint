
from googleapiclient.errors import HttpError

import json
import dataclasses

from src.Google import sheets
from src.database import initfirebase


cache = {}


spreadsheet_id = "1iC75ObLb5ZvJ4NedUmnA5O98XGVNYno0IeJYFg2DVZ8"
SAMPLE_RANGE_NAME = "Tasks!A2:I"


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


def main():
    try:
        epic_sheet = sheets.get_sheet("Epic", spreadsheet_id)
        tasks_sheet = sheets.get_sheet("Tasks", spreadsheet_id)

        task_list = []

        epic_data = sheets.transform_to_epics(epic_sheet)

        if epic_data:
            for task in tasks_sheet:
                task_object = task.to_task()
                task_list.append(task_object.__dict__)
            epic_data.tasks = task_list

        epic_json = json.dumps(epic_data, cls=EnhancedJSONEncoder, indent=4)
        task_json = json.dumps(task_list, cls=EnhancedJSONEncoder, indent=4)
        print(epic_json)
        print(task_json)

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
