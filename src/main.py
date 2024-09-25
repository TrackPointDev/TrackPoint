import sys
  
# adding src to the system path
sys.path.insert(0, '/workspaces/TrackPoint/src')

from database import setup_database

spreadsheet_id = "1iC75ObLb5ZvJ4NedUmnA5O98XGVNYno0IeJYFg2DVZ8"     # ID of the current spreadsheet.
db_collection = "kevintest"

def main():
    # Run setup only once to initialize the database if needed.
    setup_database(spreadsheet_id, db_collection)


if __name__ == "__main__":
    main()

