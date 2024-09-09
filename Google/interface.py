from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from Google import authenticate_service


cache = {}

scopes = [
        "https://www.googleapis.com/auth/spreadsheets.readonly"
    ]

spreadsheet_id = "1iC75ObLb5ZvJ4NedUmnA5O98XGVNYno0IeJYFg2DVZ8"
SAMPLE_RANGE_NAME = "Tasks!A2:I"


def main():

    creds = authenticate_service()

    try:
        service = build("sheets", "v4", credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=spreadsheet_id, range=SAMPLE_RANGE_NAME)
            .execute()
        )
        values = result.get("values", [])

        if not values:
            print("No data found.")
            return

        print("Title, Comments, Issue ID, Priority, Description, Story Point, Created, Updated")
        for row in values:
            if not row:
                print("N/A")
                continue
            # Print columns A and E, which correspond to indices 0 and 4.
            print(f"{row[0]}, {row[1]}, {row[2]}")
    except HttpError as err:
        print(err)


if __name__ == "__main__":
    main()

