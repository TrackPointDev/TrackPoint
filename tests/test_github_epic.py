import unittest
from unittest.mock import patch, MagicMock
import httpx

class TestCreateGithubIssues(unittest.TestCase):
    def setUp(self):
        # Setup any necessary data for the tests
        self.owner = "test_owner"
        self.repo = "test_repo"
        self.token = "test_token"
        self.tasks = [{"title": "Test Issue", "description": "Test Description", "priority": "High", "story_point": 5, "comments": "Test comment"}]

    @patch('httpx.post')
    def test_create_issues_success(self, mock_post):
        # Simulate a successful response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.text = "Issue created successfully"
        mock_post.return_value = mock_response

        # Call the function
        self.create_issues()

        # Assert that the post request was made with the correct parameters
        mock_post.assert_called_once_with(
            f"https://api.github.com/repos/{self.owner}/{self.repo}/issues",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "X-GitHub-Api-Version": "2022-11-28"
            },
            json={
                "title": "Test Issue",
                "body": self.format_body(self.tasks[0])
            }
        )

    @patch('httpx.post')
    def test_create_issues_failure(self, mock_post):
        # Simulate a failed response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response

        # Call the function
        self.create_issues()

        # Assert that the post request was made
        mock_post.assert_called_once()

    @patch('httpx.post')
    def test_create_github_issues_http_error(self, mock_post):
        # Simulate an HTTP error
        mock_post.side_effect = httpx.HTTPError("An error occurred")

        # Call the function
        self.create_issues()

        # Assert that the post request was attempted
        mock_post.assert_called_once()

    def create_issues(self):
        # This is a simplified version of your function for testing purposes
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/issues"
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        for task in self.tasks:
            data = {
                "title": task.get("title", ""),
                "body": self.format_body(task),
            }

            try:
                response = httpx.post(url, headers=headers, json=data)
                if response.status_code == 201:
                    print(f"Issue created successfully!\n Response: {response.text}\n")
                else:
                    print(f"Failed to create issue: \n{response.status_code}, {response.text}\n")
            except httpx.HTTPError as exc:
                print(f"An error occurred: {exc}")

    def format_body(self, task):
        body = (
            f"**Description:** {task.get('description', 'No description provided')}\n\n"
            f"**Priority:** {task.get('priority', 'No priority specified')}\n\n"
            f"**Story Point:** {task.get('story_point', 'Not estimated')}\n\n"
            f"**Comments:** {task.get('comments', 'No comments')}\n"
        )
        return body

if __name__ == '__main__':
    unittest.main()
