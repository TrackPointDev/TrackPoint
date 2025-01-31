from database.setup import setup_database
from database.manager import DatabaseManager
from epics.github_epic import github_epic
from epics.ado_epic import ado_epic
from secret_manager import access_secret_version

#TODO create a config or env file for these
class Config:
    def __init__(self):
        self.spreadsheet_id = "1o5JoaPwq7uP9oYs9KuhFBc9MJP6JybIhaLRUscgame8"
        self.db_collection = "kevintest"
        self.db_document = "hey123"
        self.owner = "TrackPointDev"
        self.repo = "TrackPointTest"
        self.project_id = "trackpointdb"
        self.gh_secret_id = "hamsterpants-github-pat"
        self.ado_secret_id = "az-devops-pat"
        self.gh_version_id = "latest"

#TODO create a test for this
def github_epic_test(config):
    db_manager = DatabaseManager(config.db_collection, config.db_document)

    setup_database(config.spreadsheet_id, db_manager)

    epic = db_manager.fetch_database()

    token = access_secret_version(config.project_id, config.gh_secret_id, config.gh_version_id)

    gh_epic = github_epic(config.owner, config.repo, token, epic['title'], epic['problem'], epic['feature'], epic['value'])
    
    for task in epic['tasks']:
        gh_epic.add_task(task)

    print("Creating issues")
    gh_epic.create_issues()

    print("Getting issues")
    print(gh_epic.get_issues())

    print("Getting tasks")
    print(gh_epic.get_tasks())

    input("Press enter to update DB")
    db_manager.update_db(gh_epic.get_epic())

    taskwithid = db_manager.get_task_with_id(70)
    print("f: Task with id: ", taskwithid)

    taskwithtitle = db_manager.get_task_with_title("TEST TEST TEST")
    print("f: Task with title: ", taskwithtitle)

"""     print("Deleting all issues")
    gh_epic.close_all_issues() """

#TODO create a test for this
def ado_epic_test(config):
    db_manager = DatabaseManager(config.db_collection, config.db_document)
    setup_database(config.spreadsheet_id, db_manager)
    epic = db_manager.fetch_database()
    token = access_secret_version(config.project_id, config.ado_secret_id, config.gh_version_id)
    az_epic = ado_epic("TrackPointDev", "TrackPoint", token, epic['title'], epic['problem'], epic['feature'], epic['value'])
    
    for task in epic['tasks']:
        az_epic.add_task(task)

    print("Creating issues")
    az_epic.create_issues()

    print("Getting issues")
    print(az_epic.get_issues())

    print("Getting tasks")
    print(az_epic.get_tasks())

    input("Press enter to update DB")
    db_manager.update_db(az_epic.get_epic())

    taskwithid = db_manager.get_task_with_id(70)
    print("f: Task with id: ", taskwithid)

    taskwithtitle = db_manager.get_task_with_title("TEST TEST TEST")
    print("f: Task with title: ", taskwithtitle)

    input("Press enter to continue")
    print("Deleting epic")
    db_manager.delete_epic()

def main():
    config = Config()

    #github_epic_test(config)
    ado_epic_test(config)


if __name__ == "__main__":
    main()

