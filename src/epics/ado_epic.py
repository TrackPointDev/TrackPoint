
import time
import httpx
import urllib 
from epics.base_epic import BaseEpic

class ado_epic(BaseEpic):
    def __init__(self, organization, project, pat, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.organization = organization
        self.project = project
        self.pat = pat

    def start(self):
        print("Start the ADO Epic")

    def create_issues(self):
        url = f"https://dev.azure.com/{self.organization}/{self.project}/_apis/wit/workitems/$task?api-version=7.1"
        for task in self.tasks:
            data = [
                    {
                        "op": "add",
                        "path": "/fields/System.Title",
                        "from": None,
                        "value": task.get("title", "")
                    },
                    {
                        "op": "add",
                        "path": "/fields/System.Description",
                        "from": None,
                        "value": self.format_body(task)
                    }
                ]

            try:
                with httpx.Client() as client:
                    response = client.post(
                        url,
                        json=data,
                        headers={'Content-Type': 'application/json-patch+json'},
                        auth=('', self.pat)
                    )

                if response.status_code == 200 or response.status_code == 201:
                    print(f"Issue created successfully!\n Response: {response}\n")
                    issue_id = response.json().get("id")
                    task["issueID"] = issue_id
                else:
                    print(f"Failed to create issue: \n{response}\n")
                   
            except httpx.HTTPError as exc:
                print(f"An error occurred: {exc}")

            print(task)

            time.sleep(1) # Add a delay to avoid hitting the rate limit

    ## Forced to make two requests to get the work item details becuase of ADO API limitations i think
    def get_issues(self):
         #Query Work Item IDs using WIQL
        wiql_url = f"https://dev.azure.com/{self.organization}/{self.project}/_apis/wit/wiql?api-version=7.1"
        wiql_query = {
            "query": "Select [System.Id], [System.Title], [System.Description] From WorkItems Where [System.WorkItemType] = 'Task'"
        }

        try:
            with httpx.Client() as client:
                response = client.post(
                    wiql_url,
                    json=wiql_query,
                    headers={'Content-Type': 'application/json'},
                    auth=('', self.pat)
                )

            if response.status_code == 200:
                work_item_ids = [item['id'] for item in response.json()['workItems']]
                print(f"Successfully retrieved issues!\n Response: {work_item_ids}\n")
                self.fetch_work_item_details(work_item_ids)
            else:
                print(f"Failed to retrieve issues: \n{response}\n")
        except httpx.HTTPError as exc:
            print(f"An error occurred: {exc}")

    #TODO some implementation with tasks list
    def fetch_work_item_details(self, work_item_ids):
        work_item_url = f"https://dev.azure.com/{self.organization}/{self.project}/_apis/wit/workitemsbatch?api-version=7.1"
        data = {
            "ids": work_item_ids,
            "fields": ["System.Id", "System.Title", "System.Description"]
        }
        try:
            with httpx.Client() as client:
                response = client.post(
                    work_item_url,
                    headers={'Content-Type': 'application/json'},
                    json = data,
                    auth=('', self.pat)
                )
            if response.status_code == 200:
                work_items = response.json()['value']
                print(f"Successfully retrieved work item details!")
                for work_item in work_items:
                    work_item_id = work_item['id']
                    title = work_item['fields'].get('System.Title', 'No Title')
                    description = work_item['fields'].get('System.Description', 'No Description')
                    print(f"Work Item ID: {work_item_id}")
                    print(f"Title: {title}")
                    print(f"Description: {description}\n")
            else:
                print(f"Failed to retrieve work item details: \n{response}\n")
        except httpx.HTTPError as exc:
            print(f"An error occurred: {exc}")

    def delete_issue(self):
        pass

    def load_json(self, file_path):
        pass

    def save_json(self, file_path):
        pass
    
    def format_body(self, task):
        # Format the body of the Azure DevOps issue with task details using HTML for bold and line breaks
        body = (
            f"<b>Description:</b><br>{task.get('description', 'No description provided')}<br><br>"
            f"<b>Priority:</b><br>{task.get('priority', 'No priority specified')}<br><br>"
            f"<b>Story Point:</b><br>{task.get('story_point', 'Not estimated')}<br><br>"
            f"<b>Comments:</b><br>{task.get('comments', 'No comments')}<br>"
        )
        return body