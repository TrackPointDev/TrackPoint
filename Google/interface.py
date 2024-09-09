
from googleapiclient.errors import HttpError

import json
import dataclasses

from Google import sheets


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
        task_list = []
        tasks_sheet = sheets.get_sheet("Tasks", spreadsheet_id)

        for task in tasks_sheet:
            task_object = task.to_task()
            task_list.append(task_object)

        json_task = json.dumps(task_list, cls=EnhancedJSONEncoder, indent=4)
        print(json_task)
    except HttpError as err:
        print(err)


if __name__ == "__main__":
    main()
