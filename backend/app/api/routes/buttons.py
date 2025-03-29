"""
Routes for Button CRUD operations.
"""

import uuid
from typing import Any

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Button,
    ButtonCreate,
    ButtonPublic,
    ButtonsPublic,
    ButtonUpdate,
    Message,
)
from fastapi import APIRouter, HTTPException, status
from sqlmodel import func, select

router = APIRouter(prefix="/buttons", tags=["buttons"])


@router.get("/", response_model=ButtonsPublic)
def read_buttons(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve all Buttons in the database. Depending on the user's role,
    filter the results.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(  # pylint: disable=E1102
            Button
        )
        count = session.exec(count_statement).one()
        statement = select(Button).offset(skip).limit(limit)
        buttons = session.exec(statement).all()
    else:
        # If not a superuser, filter buttons by the current user's ID
        count_statement = (
            select(func.count())  # pylint: disable=E1102
            .select_from(Button)
            .where(Button.created_by == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Button)
            .where(Button.created_by == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        buttons = session.exec(statement).all()

    return ButtonsPublic(data=buttons, count=count)


@router.get("/{id}", response_model=ButtonPublic)
def read_button(
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,  # pylint: disable=redefined-builtin
) -> Any:
    """
    Get a Button by its ID.
    """
    button = session.get(Button, id)
    if not button:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Button not found"
        )
    if not current_user.is_superuser and (button.created_by != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient permissions"
        )
    return button


@router.post("/", response_model=ButtonPublic)
def create_button(
    *, session: SessionDep, current_user: CurrentUser, button_in: ButtonCreate
) -> Any:
    """
    Create new Button.
    """
    button = Button.model_validate(button_in, update={"created_by": current_user.id})
    session.add(button)
    session.commit()
    session.refresh(button)
    return button


@router.put("/{id}", response_model=ButtonPublic)
def update_button(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,  # pylint: disable=redefined-builtin
    button_in: ButtonUpdate,
) -> Any:
    """
    Update an existing Button, if the user has permission.
    """
    button = session.get(Button, id)
    if not button:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Button not found"
        )
    if not current_user.is_superuser and (button.created_by != current_user.id):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="Insufficient permissions"
        )
    update_dict = button_in.model_dump(exclude_unset=True)
    button.sqlmodel_update(update_dict)
    session.add(button)
    session.commit()
    session.refresh(button)
    return button


@router.delete("/{id}")
def delete_button(
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,  # pylint: disable=redefined-builtin
) -> Message:
    """
    Delete a Button, if the user has permission.
    """
    button = session.get(Button, id)
    if not button:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Button not found"
        )
    if not current_user.is_superuser and (button.created_by != current_user.id):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="Insufficient permissions"
        )
    session.delete(button)
    session.commit()
    return Message(message="Button deleted successfully")
