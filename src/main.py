import sys
import json
  
# adding src to the system path
sys.path.insert(0, '/workspaces/TrackPoint/src')

from database.setup import setup_database
from database.manager import fetch_database
from github_epic import github_epic
from secret_manager import access_secret_version

spreadsheet_id = "1iC75ObLb5ZvJ4NedUmnA5O98XGVNYno0IeJYFg2DVZ8"     # ID of the current spreadsheet.
db_collection = "epics"
db_document = "MVP for TrackPoint"
owner = "TrackPointDev"
repo = "TrackPointTest"

def main():
    # Run setup only once to initialize the database if needed.
    # setup_database(spreadsheet_id, db_collection)
    data = fetch_database(db_collection, db_document)
    #print(data)
    tasks_with_title = [task for task in data['tasks'] if task.get('title')]

    # Create an instance of the github_epic class should maybe be moved to the database manager or smth
    #small change
    project_id = "trackpointdb"
    secret_id = "hamsterpants-github-pat"
    version_id = "latest"
    token = access_secret_version(project_id, secret_id, version_id)

    epic_title = data['title']
    epic_problem = data['problem']
    epic_feature = data['feature']
    epic_value = data['value']

    _github_epic = github_epic(owner, repo, token, epic_title, epic_problem, epic_feature, epic_value)
    for task in tasks_with_title:
        _github_epic.add_task(task)
    
    print(_github_epic.get_tasks())

    #Outcommented to avoid creating issues
    #_github_epic.create_github_issues()

if __name__ == "__main__":
    main()

