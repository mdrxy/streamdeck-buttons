"""
Routes for private API endpoints, such as user creation. These endpoints
are only available when the environment is set to "local".
"""

from typing import Any

from app.api.deps import SessionDep
from app.core.security import get_password_hash
from app.models import User, UserPublic
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["private"], prefix="/private")


class PrivateUserCreate(BaseModel):
    """
    Pydantic model to speficy the required fields for user creation.

    TODO: consider moving this to the models module?
    """

    email: str
    password: str
    full_name: str
    is_verified: bool = False


@router.post("/users/", response_model=UserPublic)
def create_user(user_in: PrivateUserCreate, session: SessionDep) -> Any:
    """
    Create a new user.
    """

    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
    )

    session.add(user)
    session.commit()

    return user
