import sys
  
# adding src to the system path
sys.path.insert(0, '/workspaces/TrackPoint/src')

from database.setup import setup_database
from database.manager import fetch_database

spreadsheet_id = "1iC75ObLb5ZvJ4NedUmnA5O98XGVNYno0IeJYFg2DVZ8"     # ID of the current spreadsheet.
db_collection = "kevintest"
db_document = "MVP for TrackPoint"

def main():
    # Run setup only once to initialize the database if needed.
    # setup_database(spreadsheet_id, db_collection)
    data = fetch_database(db_collection, db_document)
    print(data)


if __name__ == "__main__":
    main()

