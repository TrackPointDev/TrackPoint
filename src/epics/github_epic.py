
import time
import httpx 
from src.epics.base_epic import BaseEpic

class github_epic(BaseEpic):
    def __init__(self, owner, repo, token, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.owner = owner
        self.repo = repo
        self.token = token
        self.tasks = []  # Initialize empty tasks list
        self.issues_url = f"https://api.github.com/repos/{owner}/{repo}/issues"
        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28"}

    
    def create_issues(self):
        # Create GitHub issues for each task
        for task in self.tasks:
            data = {
                "title": task.get("title", ""),
                "body": self.format_body(task),
            }
  
            try:
                response = httpx.post(self.issues_url, headers=self.headers, json=data)
                # Use if-else to handle HTTP response status codes
                if response.status_code == 201:
                    print(f"Issue created successfully!\n Response: {response.text}\n")
                    issue_id = response.json().get("number")
                    task["issueID"] = issue_id
                else:
                    print(f"Failed to create issue: \n{response.status_code}, {response.text}\n")
            except httpx.HTTPError as exc:
                # Use except to handle exceptions during the request
                print(f"An error occurred: {exc}")
            
            time.sleep(1)  # Add a delay to avoid hitting the rate limit
            
    def format_body(self, task):
        # Format the body of the GitHub issue with task details
        body = (
            f"**Description:** {task.get('description', 'No description provided')}\n\n"
            f"**Priority:** {task.get('priority', 'No priority specified')}\n\n"
            f"**Story Point:** {task.get('story_point', 'Not estimated')}\n\n"
            f"**Comments:** {task.get('comments', 'No comments')}\n"
        )
        return body
    
    def start(self):
        print("Start the GitHub Epic")
    
    #TODO some implementation with tasks list
    def get_issues(self):
        try:
            response = httpx.get(self.issues_url, headers=self.headers)
            if response.status_code == 200:
                issues = response.json()
                print(f"Retrieved issues successfully!\n Issues: {issues}\n")
                for issue in issues:
                    print(f"Issue Number: {issue['number']}")
                    print(f"Issue: {issue['title']}")
                    print(f"Body: {issue['body']}\n")
            else:
                print(f"Failed to retrieve issues: \n{response.status_code}, {response.text}\n")
        except httpx.HTTPError as exc:
            print(f"An error occurred: {exc}")
            

    def delete_issue(self, title):
        pass
    def load_json(self, file_path):
        pass
    def save_json(self, file_path):
        pass    

    def close_all_issues(self):
        while True:
            page = 1
            response = httpx.get(self.issues_url, headers=self.headers, params={'state': 'open', 'page': page})
            issues = response.json()

            if not issues:
                break

            for issue in issues:
                issue_number = issue['number']
                delete_url = f"{self.issues_url}/{issue_number}"
                delete_response = httpx.patch(delete_url, headers=self.headers, json={"state": "closed"})
                if delete_response.status_code == 200:
                    print(f"Issue {issue_number} closed successfully!")
                else:
                    print(f"Failed to close issue {issue_number}: {delete_response.status_code}, {delete_response.text}")
            
            page += 1
            time.sleep(1)