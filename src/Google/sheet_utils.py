import time

from itertools import zip_longest
from typing import Dict, List, Any, Union, Optional
from googleapiclient.discovery import build

from Google import authenticate_service
from database.models import Task, Epic
from Google.sheets import get_sheet, get_sheets_api, create_text_cell, create_number_cell, create_dropdown_cell

from fastapi import Request, HTTPException

class SheetUtils:
    """This class contains utility methods for writing to Google Sheets."""

    def __init__(self, request: Request):
        self.request = request
        self.logger = request.app.state.logger
        self.client = request.app.state.client
        self.db = request.app.state.db
        self.service = authenticate_service()
        self.tasks_to_add = []

    def add_task(self, task: Task, batch: Optional[bool] = False, limit: int = None, spreadsheetID: str = None):
        """Method for adding a taks to the Google Sheets document.
        Supports batch processing of tasks."""

        if batch is True:
            print(f"Appended {task.title} to the list.")
            self.tasks_to_add.append(task.model_dump(mode='json'))

            if len(self.tasks_to_add) >= limit:
                self.batch_process_tasks(self.tasks_to_add, limit)
        else:
            body = self.build_new_task_row_request(task, spreadsheetID)
            self.update_sheets_data(body, "adding task", spreadsheetID)
    
    def update_task(self, task: Task, spreadsheetID: str):
        """Method for updating a task in the Google Sheets document."""

        body = self.update_task_row_request(task, spreadsheetID)
        self.update_sheets_data(body, "updating task", spreadsheetID)

    def build_new_task_row_request(self, task: Task, spreadsheetID: str) -> list[dict]:
        """
        Builds the list of request bodies for adding a new task row in the Sheets document.
        The row will have data validation - that is, drop-downs and checkboxes.

        :param task: The task to add.
        :param spreadsheetID: The ID of the spreadsheet.
        :return: List of dictionaries, each dict being a request to Google Sheets API.
        """
        
        sheet_name = "Tasks"
        sheet_id = self.get_sheet_id_by_name(sheet_name, spreadsheetID)
        column_mapping = self.map_to_column(task)

        row_index = len(get_sheet(sheet_name, spreadsheetID).rows) + 1
        # Construct the individual request components
        append_cells_request = {
            "appendCells": {
                "sheetId": sheet_id,
                "fields": "*",
                "rows": [{
                    "values": self.map_task_to_column_values(task, column_mapping, spreadsheetID)
                }]
            }
        }

        update_dimension_request = {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sheet_id,
                    "dimension": "ROWS",
                    "startIndex": row_index,
                    "endIndex": row_index + 1
                },
                "properties": {
                    # By default, the height of the row scales dynamically with the
                    # contents of the cells. This ensures a static height.
                    "pixelSize": 21
                },
                "fields": "pixelSize"
            }
        }

        # Encapsulate all request actions in a single list.
        return [append_cells_request, update_dimension_request]
    
    def update_task_row_request(self, task: Task, spreadsheetID: str):
        """
        Builds a list of update requests for several columns for an existing profile row in the Sheets document.
        Retries the operation if a required column is added dynamically.
        """
        sheet_name = "Tasks"
        sheet_id = self.get_sheet_id_by_name(sheet_name, spreadsheetID)
        row_index = None
        sheet = get_sheet(sheet_name, spreadsheetID)

        for i, row in enumerate(sheet.rows, start=1):
            if row["title"] == task.title:
                row_index = i
                break

        if row_index is None:
            raise Exception(f"Row with title '{task.title}' not found in sheet '{sheet_name}'")
    
        header_data = {
            "title": task.title,
            "duplicate / comments": task.comments,
            "issue id": task.issueID,
            "priority": task.priority,
            "description": task.description,
            "story point": task.story_point,
        }

        column_indexes = self.find_column_indexes(sheet, header_data.keys())

        print(f"Updating task '{task.title}' in row {row_index}...")
        update_requests = []
        for header_name, data in header_data.items():
            column_index = column_indexes.get(header_name, None)
            if data is None or column_index is None:
                continue

            user_entered_value = {}
            if isinstance(data, int):
                user_entered_value["numberValue"] = data
            else:
                user_entered_value["stringValue"] = str(data)

            update_requests.append({
                "updateCells": {
                    "rows": [{
                        "values": [{"userEnteredValue": user_entered_value}]
                    }],
                    "fields": "userEnteredValue",
                    "start": {
                        "sheetId": sheet_id,
                        "rowIndex": row_index,
                        "columnIndex": column_index - 1  # Adjust for 0-based indexing
                    }
                }
            })

        update_requests.append({
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sheet_id,
                    "dimension": "ROWS",
                    "startIndex": row_index - 1,
                    "endIndex": row_index
                },
                "properties": {
                    "pixelSize": 21
                },
                "fields": "pixelSize"
            }
        })

        return update_requests

    def map_task_to_column_values(self, task: Task, column_mappings, spreadsheetID: str):
        values = []

        for header in get_sheet("Tasks", spreadsheetID).headers:
            column_key = header.lower()

            if column_key in column_mappings:
                values.append(column_mappings[column_key](task.model_dump(mode='json')))
            else:
                values.append(create_text_cell(None))
                if header:
                    print(f"Skipping unknown column '{header}'")

        return values

    def map_to_column(self, object: Union[Epic, Task]):
        if isinstance(object, Task):
            columns_to_map = {
                "title": lambda task: create_text_cell(task["title"]),
                "duplicate / comments": lambda task: create_text_cell(task["comments"]),
                "description": lambda task: create_text_cell(task["description"]),
                "issue id": lambda task: create_number_cell(task["issueID"]),
                "priority": lambda task: create_dropdown_cell(initial_content=task["priority"]),
                "story point": lambda task: create_number_cell(task["story_point"]),
            }
            return columns_to_map
        elif isinstance(object, Epic):
            columns_to_map = {
                "Title": lambda epic: create_text_cell(epic["title"]),
                "Problem": lambda epic: create_text_cell(epic["problem"]),
                "Feature": lambda epic: create_text_cell(epic["feature"]),
                "Value": lambda epic: create_text_cell(epic["value"]),
            }
            return columns_to_map

    def batch_process_tasks(self, task_list: List[Task], limit):
        """Batch process tasks to be added to the Google Sheets epic."""

        # Each task has 2 requests, so we get a list of lists
        batch_requests: list[list[dict]] = [self.build_new_task_row_request(task) for task in task_list[:limit]]
        # Flatten the list of lists into a list
        batch_requests: list[dict] = [request for requests in batch_requests for request in requests]

        if batch_requests:
            self.update_sheets_data(batch_requests, "adding tasks")
        added = len(batch_requests)/2
        print(f"Added {int(added)} tasks to database")

    def update_sheets_data(self, requests: list[dict[str, Any]], operation: str, spreadsheetID: str) -> None:
        """
        Updates Google Sheets data with the given requests.

        :param requests: The list of requests to execute.
        :param operation: The operation being performed (e.g., "adding tasks", "updating").
        """
        body = {"requests": requests}

        print(f"Updating Google Sheets with {operation}...")

        for attempt in range(5):
            try:
                get_sheets_api().batchUpdate(spreadsheetId=spreadsheetID, body=body).execute()
                return
            except HTTPException as e:
                print(f"Error during {operation}: {e}")
                if attempt < 4:
                    print("Retrying in 60 seconds...")
                    time.sleep(60)

        raise Exception(f"Failed {operation} after 5 attempts.")
    
    def get_sheet_id_by_name(self, sheet_name: str, spreadsheetID: str) -> Optional[int]:
        """
        Returns the ID of the sheet with the given name, or None if it doesn't exist.
        """

        sheet = get_sheets_api()

        spreadsheet = sheet.get(spreadsheetId=spreadsheetID).execute()
        for sheet in spreadsheet.get('sheets'):
            if sheet['properties']['title'] == sheet_name:
                sheet_name = sheet['properties']['sheetId']
                return sheet_name

        return None
    
    def find_column_indexes(self, sheet, header_names):
        """
        Finds the column indexes for the specified header names in the given sheet.
        Returns a dictionary mapping header names to their column indexes.
        """
        print(f"Finding column indexes for headers: {header_names}")
        column_indexes = {}
        for i, header in enumerate(sheet.headers, start=1):
            if header.lower() in header_names:
                column_indexes[header.lower()] = i
        return column_indexes
    
    def remove_task(self, task: Task, spreadsheetID: str):
        """Removes the given tasks from the sheet."""
        if not task:
            return

        row = self.get_row_with_task(task, spreadsheetID)
        delete_row_requests = self.delete_row_request(row, spreadsheetID) 

        get_sheets_api().batchUpdate(
            spreadsheetId=spreadsheetID,
            body={"requests": delete_row_requests}
        ).execute()


    def delete_row_request(self, row, spreadsheetID: str) -> dict:
        """Returns a request body for deleting a row."""
        sheet_id = self.get_sheet_id_by_name("Tasks", spreadsheetID=spreadsheetID)

        return {
            "deleteDimension": {
                "range": {
                    "sheetId": 0 if sheet_id is None else sheet_id,
                    "dimension": "ROWS",
                    "startIndex": row - 1,
                    "endIndex": row
                }
            }
        }
    
    def get_row_with_task(self, task: Task, spreadsheetID: str = None):
        """Returns the row number of the given task, or raises IndexError if it doesn't exist."""
        return get_sheet(sheet_name="Tasks", spreadsheet_id=spreadsheetID).row_index("title", task.title)
    

