from typing import Annotated, Union
from fastapi import APIRouter, HTTPException, Header

from database.manager import DatabaseManager
from database.models import Epic, User

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
)

db = DatabaseManager("Users")

@router.post("")
async def create_user(user: User):
    """
    Creates a new user in the Firestore database.

    Args:
        user (User): The user to be created.
    Returns:
        dict: A dictionary containing the status and message of the operation.
    """
    print(f"Received user: {user.name}")

    try:
        db.create_user(user.model_dump(mode='json'))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

    return {"status": 200, "message": f"User with name {user.name} created successfully."}

@router.get("")
async def get_users(userName: Annotated[str | None, Header()] = None):
    """
    Get either a specific user or the entire list of users in the Firestore database.

    Args:
        userName (str): Optional name for the user to be retrieved. If none is provided, all users will be returned.
    Returns:
        user (dict or list): A dictionary containing the user data if a user name is provided, else a list of all users.
    Raises:
        HTTPException: If an error occurs during the fetch operation, it will be caught and a 500 error will be raised.
    """
    if userName:
        try:
            user = db.get_user(userName)
            return user if user else {"status": 404, "message": "User not found."}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    try:
        return db.get_all_users()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    
@router.put("")
async def update_user(user: User):
    """
    Updates an existing user in the Firestore database.

    Args:
        user (User): The user to be updated.
    Returns:
        dict: A dictionary containing the status and message of the operation.
    """
    print(f"Received user: {user.name}")

    try:
        db.update_user(user.model_dump(mode='json'))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

    return {"status": 200, "message": f"User with name {user.name} updated successfully."}

@router.delete("")
async def delete_user(userName: Annotated[str | None, Header()]):
    """
    Deletes a user from the Firestore database.

    Args:
        userName (str): The name of the user to be deleted.
    Returns:
        dict: A dictionary containing the status and message of the operation.
    """
    print(f"Deleting user: {userName}")

    try:
        db.delete_user(userName)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

    return {"status": 200, "message": f"User with name {userName} deleted successfully."}