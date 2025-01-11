from typing import Annotated, Union
from fastapi import APIRouter, Request, HTTPException, Header

from database.manager import DatabaseManager
from database.models import Epic


router = APIRouter(
    prefix="/epics",
    tags=["Epics"],
    responses={404: {"description": "Not found"}},
)

db = DatabaseManager("epics", "showcase")

class EpicManager:
    def __init__(self, request: Request):
        self.client = request.app.state.client
        self.logger = request.app.state.logger

@router.post("")
async def create_epic(epic: Epic):
    """
    Creates a new epic in the Firestore database.

    Args:
        epic (Epic): The epic to be created.
    Returns:
        dict: A dictionary containing the status and message of the operation.
    """
    print(f"Received epic: {epic.title}")

    try:
        db.create_epic(epic.model_dump(mode='json'))
    except Exception as e:
        router.app.state.logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

    return {"status": 200, "message": f"Epic with title {epic.title} created successfully."}

@router.get("")
async def get_epics(epicTitle: Annotated[str | None, Header()] = None):
    """
    Get either a specific epic or the entire list of epics in the Firestore database.

    Args:
        epicTitle (str): Optional title for the epic to be retrieved. If none is provided, all epics will be returned.
    Returns:
        epic (dict or list): A dictionary containing the epic data if an epic title is provided, else a list of all epics.
    Raises:
        HTTPException: If an error occurs during the fetch operation, it will be caught and a 500 error will be raised.
    """
    if epicTitle:
        try:
            epic = db.get_epic(epicTitle)
            return epic.model_dump(mode='json') if epic else {"status": 404, "message": "Epic not found."}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    try:
        return db.get_all_epics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    
    

@router.put("")
async def update_epic(epicTitle: Annotated[str | None, Header()], epic: Epic):
    """
    Updates a given epic in the Firestore database.

    Args:
        epictitle (str): The title of the epic to be updated.
        epic (Epic): The entire new epic obejct. Current implementation does not support partial updates.
    Returns:
        dict: A dictionary containing the status and message of the operation.
    Raises:
        HTTPException: If an error occurs during the update operation, it will be caught and a 500 error will be raised.
    """

    if not epicTitle:
        raise HTTPException(status_code=400, detail="Please provide the title of the epic to be updated.")
    
    try:
        db.update_epic(epicTitle, epic)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    return {"status": 200, "message": f"Epic with title '{epicTitle}' updated successfully."}

@router.delete("")
async def delete_epic(epicTitle: Annotated[str | None, Header()]):
    """
    Delete a specific epic in the Firestore database.

    Args:
        epicTitle (str): The title of the epic to be deleted.
    Returns:
        dict: A message indicating the status of the operation.
    Raises:
        HTTPException: If an error occurs during the delete operation, it will be caught and a 500 error will be raised.
    """

    if not isinstance(epicTitle, str):
        raise HTTPException(status_code=400, detail="Please provide the title of the epic to be deleted.")
    
    try:
        db.delete_epic(epicTitle)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    return {"status": 200, "message": "Epic deleted successfully."}