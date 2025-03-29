"""
CRUD operations for the application.
"""

import uuid
from typing import Any

from app.core.security import get_password_hash, verify_password
from app.models import Button, ButtonCreate, User, UserCreate, UserUpdate
from sqlmodel import Session, select


def create_user(*, session: Session, user_create: UserCreate) -> User:
    """
    Create a new user in the database.
    This function takes a user object and hashes the password.
    """
    hashed = get_password_hash(user_create.password)
    db_obj = User(**user_create.model_dump())
    db_obj.hashed_password = hashed
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    """
    Update a user in the database.
    This function takes a user object and an update object.
    """
    user_data = user_in.model_dump(exclude_unset=True)
    if "password" in user_data:
        user_data["hashed_password"] = get_password_hash(user_data.pop("password"))

    for field, value in user_data.items():
        setattr(db_user, field, value)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    """
    Get a user by email address.
    """
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    """
    Authenticate a user by email and password.
    """
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def create_button(
    *, session: Session, button_in: ButtonCreate, created_by: uuid.UUID
) -> Button:
    """
    Create a new button in the database.
    This function takes a button object and the ID of the user
    who created it.
    """

    # Instantiate the Button using the dictionary data from ButtonCreate
    db_button = Button(**button_in.model_dump())
    # Then explicitly set the created_by field.
    db_button.created_by = created_by
    session.add(db_button)
    session.commit()
    session.refresh(db_button)
    return db_button
