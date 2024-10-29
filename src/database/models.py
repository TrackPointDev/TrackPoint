from pydantic import BaseModel, Field
from typing import Optional, Union

class Task(BaseModel):
    title: str = Field(..., description="The title of the task.")
    comments: Optional[str] = Field(None, description="Comments on the task.")
    description: str = Field(..., description="A description of the task.")
    issueID: Optional[int] = Field(None, description="The issue ID associated with the task.")
    priority: str = Field(..., description="The priority level of the task.")
    story_point: int = Field(..., description="The story points assigned to the task.")
