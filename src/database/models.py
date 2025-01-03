from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, Union, List, Literal

class Task(BaseModel):
    title: Optional[str] = Field(..., description="The title of the task.")
    comments: Optional[str] = Field(None, description="Comments on the task.")
    description: Optional[str] = Field(..., description="A description of the task.")
    issueID: Optional[int] = Field(None, description="The issue ID associated with the task.")
    priority: Optional[str] = Field(..., description="The priority level of the task.")
    story_point: Optional[int] = Field(..., description="The story points assigned to the task.")
    #story_point_bid: Optional[int] = Field(None, description="The story points bid for the task.")
    #status: Optional[str] = Field(None, description="The status of the task.")
    #asignees: Optional['User'] = Field(None, description="The user assigned to the task.")

class Epic(BaseModel):
    title: str = Field(..., description="The title of the epic.")
    problem: Optional[str] = Field(..., description="The problem statement of the epic.")
    feature: Optional[str] = Field(None, description="The feature statement of the epic.")
    value: Optional[str] = Field(..., description="The value statement of the epic.")
    tasks: Optional[List[Task]] = Field(..., description="A list of tasks associated with the epic.")
    users: Optional[List['User']] = Field(None, description="A list of users associated with the epic.")

    spreadsheetId: Optional[str] = Field(None, description="The spreadsheet ID of the epic.")
    secret: Optional[str] = Field("mysecretstring1234", description="A secret field.")
    installationID: Optional[str] = Field("56537454", description="The installation ID of the epic.")
    repoOwner: Optional[str] = Field("TrackPointDev", description="The repository owner of the epic.")
    repoName: Optional[str] = Field("TrackPointTest", description="The repository name of the epic.")


class User(BaseModel):
    name: str = Field(..., description="The name of the user.")
    email: Optional[str] = Field("user@example.org", description="The email of the user.")
    role: Optional[str] = Field(None, description="The role of the user.")
    uID: Optional[str] = Field(None, description="The unique ID of the user.")
    epics: Optional[List[str]] = Field(None, description="A list of epics associated with the user.")

# Rebuild the models, such that forward refs for 'asignee' and 'users' are resolved.
Task.model_rebuild()
Epic.model_rebuild()
