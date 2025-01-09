import re
import string
import asyncio

from dataclasses import dataclass
from itertools import zip_longest
from typing import Dict, List, Union, Optional
from googleapiclient.discovery import build

from Google import authenticate_service
from database.models import Task, Epic
from plugins import PluginManager

from fastapi import Request

cache = {}

@dataclass
class Row:
    """
    Represents a row in a Google Sheet spreadsheet

    Attributes:
        index: The index of the row (as it appears in the sheet)
        values: A dictionary mapping column headers to values
    """
    index: int
    values: Dict[str, Union[str, int, None]]

    def __init__(self, index: int, values: Dict[str, str], column: str = None):
        column = clean(column)
        if column in values and isinstance(values[column], int):
            values[column] = str(values[column])

        self.index = index
        self.values = values

    def __iter__(self):
        return iter(self.values.values())

    def __contains__(self, header):
        return clean(header) in self.values

    def __getitem__(self, header: str):
        if header not in self:
            raise IndexError(f"Row {self.index} does not have a column '{header}'")
        return self.values[clean(header)]

    def has_header(self, header):
        """Returns True if the row has a column with the given header"""
        return header in self

    def to_task(self) -> Task:
        """Converts a row in the Google sheet to a Task object"""
        return Task(
            title=self.values.get("title", ""),
            comments=self.values.get("duplicate / comments", ""),
            issueID=self.values.get("issue id", ""),
            priority=self.values.get("priority", ""),
            description=self.values.get("description", ""),
            story_point=self.values.get("story point", 0)
        )


@dataclass
class Column:
    """
    Represents a column in a Google Sheet spreadsheet

    Attributes:
        header: The header of the column
        values: The values in the column (excluding the header)
    """
    header: str
    values: List[Union[str, int, None]]

    def __iter__(self):
        return iter(self.values)

    def __getitem__(self, row_index: int):
        if row_index < 0:
            raise IndexError(f"Row index {row_index} is out of bounds")
        if row_index >= len(self.values):
            raise IndexError(f"Searched for row {row_index}, but column '{self.header}' "
                             f"only has {len(self.values)} rows")
        return self.values[row_index]


@dataclass
class Sheet:
    """
    Represents a sheet in a Google Sheet spreadsheet

    Attributes:
        headers: The headers of the sheet
        rows: The rows of the sheet (zero-indexed)
    """
    headers: List[str]
    rows: List[Row]

    def __init__(self, headers: List[str], rows: List[List[str]]):
        def clean_value(value: str) -> Union[str, int, None]:
            value = value.strip()
            if value == "":
                return None
            return int(value) if _is_ascii_digit(value) else value

        rows = [[clean_value(value) for value in row] for row in rows]
        self.headers = [clean(header) for header in headers]
        self.rows = [Row(i, dict(zip_longest(self.headers, row)))
                     for i, row in enumerate(rows, start=2)]

    def __iter__(self):
        return iter(self.rows)

    def __contains__(self, header):
        return clean(header) in self.headers

    def __getitem__(self, index: Union[int, str]) -> Union[Row, Column]:
        if isinstance(index, int):
            return self.row(index)
        if isinstance(index, str):
            return self.column(index)
        raise ValueError("Index must be an integer (row) or a string (column)")

    def row(self, index: int) -> Row:
        """Returns the row at the given index (zero-indexed)"""
        if index < 0:
            raise IndexError(f"Row index {index} is out of bounds")
        if index >= len(self.rows):
            raise IndexError(f"Searched for row {index}, but sheet only has {len(self.rows)} rows")
        return self.rows[index]

    def column(self, header: str, alternatively: Optional[str] = None) -> Column:
        """
        Returns the column with the given header, or the column with the optional
        alternative header if the first header does not exist in the sheet
        """
        header = clean(header)
        if header not in self.headers:
            if alternatively is not None:
                return self.column(alternatively)
            raise IndexError(f"Sheet does not have a column '{header}'")
        return Column(header, [row[header] for row in self.rows])

    def columns(self) -> List[Column]:
        """Returns a list of all columns in the sheet"""
        return [self.column(header) for header in self.headers]

    def row_index(self, column: str, value: Union[str, int]) -> int:
        """Returns the index of the first row with the given value in the given column"""
        column = clean(column)
        if column not in self:
            raise IndexError(f"Sheet does not have a column '{column}'")
        for row in self.rows:
            if row[column] == value:
                return row.index
        raise IndexError(f"Sheet does not have a row with '{column}' = '{value}'")

    def header_index(self, header: str) -> str:
        """Returns the index (A-ZZ) of the given header"""
        return self.header_indices()[clean(header)]

    def header_indices(self) -> Dict[str, str]:
        """Returns a dictionary mapping headers to their indices (A-ZZ)"""
        def column_index(i: int) -> str:
            if i < 26:
                return string.ascii_uppercase[i]
            return string.ascii_uppercase[i // 26 - 1] + string.ascii_uppercase[i % 26]

        return {header: column_index(i) for i, header in enumerate(self.headers)}

    def has_header(self, header: str) -> bool:
        """Returns True if the sheet has a column with the given header"""
        return header in self


def transform_to_epics(sheet: Sheet, payload: Optional[dict]) -> Optional[Epic]:
    """
    Transforms a sheet into an Epic object.
    """

    # TODO: Hardcoding the indexes is utterly fucking retarded. For now it works, but refactor later

    title_index = 2
    problem_index = 3
    feature_index = 4
    value_index = 5
    column_index = "b"

    title_row = sheet.row(title_index - 1)
    problem_row = sheet.row(problem_index - 1)
    feature_row = sheet.row(feature_index - 1)
    value_row = sheet.row(value_index - 1)

    title = title_row[column_index]
    problem = problem_row[column_index]
    feature = feature_row[column_index]
    value = value_row[column_index]

    return Epic(
        title=title,
        problem=problem,
        feature=feature,
        value=value,
        tasks=[],
        users=[],
        spreadsheetId=payload.get("spreadsheetId")
    )


def get_sheet(
    sheet_name: Optional[str] = None,
    spreadsheet_id: Optional[str] = None
) -> Sheet:
    """
    Returns a Sheet object representing the sheet with the given name in the given spreadsheet.

    If sheet_name is None, the first sheet in the spreadsheet is returned.
    If spreadsheet_id is None, the spreadsheet_id ID is retrieved from the command line arguments. (NOT IMPLEMENTED).
    """

    print(f"Getting sheet {sheet_name} from spreadsheet {spreadsheet_id}")

    sheets_api = get_sheets_api()

    spreadsheet_range = _spreadsheet_range(sheet_name=sheet_name)
    all_rows = sheets_api.values().get(
        spreadsheetId=spreadsheet_id, range=spreadsheet_range
    ).execute()["values"]

    headers, rows = all_rows[0], all_rows[1:]
    sheet = Sheet(headers, rows)

    return sheet


def _spreadsheet_range(
    start_col: str = "A",
    end_col: str = "ZZ",
    start_row: int = 1,
    end_row: Optional[int] = None,
    sheet_name: Optional[str] = None,
) -> str:
    """Returns a string representing a range in a Google Sheets spreadsheet."""
    spreadsheet_range = f"{start_col}{start_row}:{end_col}"

    if end_row is not None:
        spreadsheet_range = f"{spreadsheet_range}{end_row}"
    if sheet_name is not None:
        spreadsheet_range = f"'{sheet_name}'!{spreadsheet_range}"

    return spreadsheet_range


def get_sheets_api():
    credentials = authenticate_service()
    service = build("sheets", "v4", credentials=credentials)
    sheets_api = service.spreadsheets()

    return sheets_api


def clean(value: str) -> str:
    if value is None:
        return "blank"
    return value.strip().lower()


def _is_ascii_digit(value: str) -> bool:
    """
    is_digit() and is_numeric() returns True for numeric strings like "¹³".
    This function returns True only for strings containing digits 0-9.
    """
    return bool(re.match(r'^[0-9]+$', value))

def create_text_cell(text):
    field = {"userEnteredValue": {}}
    field["userEnteredValue"]["stringValue"] = text

    return field

def create_number_cell(num):
    return {
        "userEnteredValue": {
            "numberValue": num
        }
    }

def update_existing_task_issue_ids(existing_epic: Epic, new_epic: Epic, old_value: str) -> None:
    """
    Copies issueID from existing tasks to new tasks if the title matches oldValue.
    """
    print("Updating task")
    for item in existing_epic.tasks:
        for task in new_epic.tasks:
            if old_value == item.title:
                task.issueID = item.issueID

async def handle_sheet_webhook_event(request: Request, plugin: PluginManager):
    """
    Handles a webhook event from a Google Sheet.

    Args:
        payload (dict): The payload of the webhook event.
    """

    payload = await request.json()
    db = request.app.state.db

    async def handle_epic():
        sheet_epic = db.parse_sheet(payload)
        existing_epic = db.get_epic(sheet_epic.title)

        if existing_epic is None:
            db.create_epic(sheet_epic.model_dump(mode='json'))
            await plugin.post_to_plugin(sheet_epic, "setup")
        else:
            if payload.get("sheetName") == "Tasks":
                update_existing_task_issue_ids(existing_epic, sheet_epic, payload.get("oldValue"))
                
            db.update_epic(sheet_epic.title, sheet_epic.model_dump(mode='json'))
            await plugin.post_to_plugin(sheet_epic, "update")
        
    async def handle_user():
        user = payload.get("user")
        print(f"User: {user}")

        if user["nickname"] and user["email"] is not None:
            existing_user = db.get_all_users(user["nickname"])
            if existing_user is None:
                db.create_user(user)
                print(f"Created new user: {user["nickname"]}")
            else:
                print(f"User {user["nickname"]} already exists")
        else:
            return {"status": 400, "message": "User has no nickname or email"}

    # Run both functions concurrently. Check for epics and users.
    await asyncio.gather(handle_epic(), handle_user())
    return {"status": 200, "message": "DB updated Succesfully"}
