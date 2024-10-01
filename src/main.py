import sys
import json
  
# adding src to the system path
sys.path.insert(0, '/workspaces/TrackPoint/src')

from database.setup import setup_database
from database.manager import DatabaseManager
from github_epic import github_epic
from secret_manager import access_secret_version

spreadsheet_id = "1o5JoaPwq7uP9oYs9KuhFBc9MJP6JybIhaLRUscgame8"
db_collection = "kevintest"
db_document = "MVP for TrackPoint"
owner = "TrackPointDev"
repo = "TrackPointTest"

def main():
    db_manager = DatabaseManager()
    # Run setup only once to initialize the database if needed.
    setup_database(spreadsheet_id, db_collection, db_manager) 
    data = db_manager.fetch_database(db_collection, db_document)
    #print(data)
    tasks_with_title = [task for task in data['tasks'] if task.get('title')]

    # Create an instance of the github_epic class should maybe be moved to the database manager or smth
    #small change
    project_id = "trackpointdb"
    secret_id = "hamsterpants-github-pat"
    version_id = "latest"
    token = access_secret_version(project_id, secret_id, version_id)
    print(token)

    epic_title = data['title']
    epic_problem = data['problem']
    epic_feature = data['feature']
    epic_value = data['value']

    _github_epic = github_epic(owner, repo, token, epic_title, epic_problem, epic_feature, epic_value)
    for task in tasks_with_title:
        _github_epic.add_task(task)
    
    print(_github_epic.get_tasks())

    #Outcommented to avoid creating issues
    print("Creating issues")

    _github_epic.create_issues()

    print(_github_epic.get_tasks())

    input("Press enter to update DB")
    db_manager.update_db(db_collection, db_document, _github_epic.get_epic())

    input("Press enter to continue")
    print("Deleting epic")
    #db_manager.delete_epic(db_collection, db_document)


if __name__ == "__main__":
    main()

