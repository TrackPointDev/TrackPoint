import httpx

# Note: owner/repo values might be used in multiple functions, so it might be better to move them to a config file.
# or store them as global variables in a separate module.
owner = "TrackPointDev"
repo = "TrackPointTest"

# This is a secret value, do NOT hardcode it in the code. Use environment variables instead.
github_token = "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"     # Replace with your own GitHub token, remember to give it the proper permissions.


# TODO: Make "owner" and "repo" parameters dynamic. Such that we can pass different owners/repos to the function
#  without having to hardcode it.

# TODO: Having all the parameters in the request be arguments to this function is a little cluttered. Consider
#  having two arguments as dicts, one for the header and one for the data. This would make the function call
#  cleaner and more readable. Then retrieve the relevant parameters from the dicts in the function body and
#  pass it to the request.

# TODO: Implement data validation with Pydantic to ensure proper data/types are passed to the function.
def create_github_issue(header: dict = None, data: dict = None):
    """Makes a request to the GitHub API to create an issue in the repository. Takes two dicts as arguments, one for
    the header and one for the data. These dicts are unpacked and sent to the API in a request.

    Args:
        header: The header for the request. Should contain the owner, repo and github_token.
        data: The body of the request. Contains the parameters to create the issue: title(required), body(optional),
            milestone(optional), labels(optional), assignees(optional).

    For further reading on parameter types,
    see docs: https://docs.github.com/en/rest/issues/issues?apiVersion=2022-11-28#create-an-issue"""

    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {github_token}",
        "X-GitHub-Api-Version": "2022-11-28"}

    data = {
        "title": data.get("title", ""),
        "body": data.get("body", ""),
    }

    response = httpx.post(url, headers=headers, json=data)

    if response.status_code == 201:
        print(f"Issue created successfully!\n Response: {response.text}\n")
    else:
        print(f"Failed to create issue: \n{response.status_code}, {response.text}\n")
