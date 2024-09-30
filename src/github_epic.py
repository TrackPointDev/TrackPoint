
import os
import time
import httpx 
from base_epic import BaseEpic

class github_epic(BaseEpic):
    def __init__(self, owner, repo, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.owner = owner
        self.repo = repo
        self.token = "ghp_1234567890"
        self.tasks = []  # Initialize empty tasks list


    def add_task(self, task):
        self.tasks.append(task)

    def remove_task(self, task_title):
        self.tasks = [task for task in self.tasks if task["title"] != task_title]

    def get_tasks(self):
        return self.tasks

    def load_json(self, file_path):
        # Mock JSON loading
        pass

    def save_json(self, file_path):
        # Mock JSON saving
        pass

    def edit_task(self, task_title, new_data):
        for task in self.tasks:
            if task["title"] == task_title:
                task.update(new_data)
                return True
        return False
    
    def create_github_issues(self):
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/issues"
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28"}

        for task in self.tasks:
            data = {
                "title": task.get("title", ""),
                "body": self.format_body(task),
            }
  
            try:
                response = httpx.post(url, headers=headers, json=data)
                # Use if-else to handle HTTP response status codes
                if response.status_code == 201:
                    print(f"Issue created successfully!\n Response: {response.text}\n")
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

# TODO: Having all the parameters in the request be arguments to this function is a little cluttered. Consider
#  having two arguments as dicts, one for the header and one for the data. This would make the function call
#  cleaner and more readable. Then retrieve the relevant parameters from the dicts in the function body and
#  pass it to the request.