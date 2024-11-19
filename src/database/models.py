from pydantic import BaseModel, Field
from typing import Optional, Union, List

class Task(BaseModel):
    title: str = Field(..., description="The title of the task.")
    comments: Optional[str] = Field(None, description="Comments on the task.")
    description: Optional[str] = Field(..., description="A description of the task.")
    issueID: Optional[int] = Field(None, description="The issue ID associated with the task.")
    priority: Optional[str] = Field(..., description="The priority level of the task.")
    story_point: Optional[int] = Field(..., description="The story points assigned to the task.")

class Epic(BaseModel):
    title: str = Field(..., description="The title of the epic.")
    problem: Optional[str] = Field(..., description="The problem statement of the epic.")
    feature: Optional[str] = Field(None, description="The feature statement of the epic.")
    value: Optional[str] = Field(..., description="The value statement of the epic.")
    tasks: Optional[List[Task]] = Field(..., description="A list of tasks associated with the epic.")