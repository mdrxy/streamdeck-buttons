"""
Routes for Button CRUD operations.
"""

import uuid
from datetime import datetime, timezone
from typing import Any

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Button,
    ButtonCreate,
    ButtonPublic,
    ButtonRetirement,
    ButtonRetirementsPublic,
    ButtonsPublic,
    ButtonUpdate,
    ButtonUse,
    Message,
    RetireButtonRequest,
)
from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError
from sqlmodel import delete, func, select

router = APIRouter(prefix="/buttons", tags=["buttons"])


def get_client_ip(request: Request) -> str:
    """
    Extract the client's IP address from the request.
    """
    client_ip = request.headers.get("X-Forwarded-For")
    return client_ip.split(",")[0].strip() if client_ip else request.client.host


@router.get("/", response_model=ButtonsPublic)
def list_all_buttons(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve all Buttons in the database. Depending on the role of the
    user making the request, the response may include all Buttons or
    only those created by the requesting user.
    """
    # TODO: add filtering, sorting, calculate usage count across all Buttons returned

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(  # pylint: disable=E1102
            Button
        )
        count = session.exec(count_statement).one()
        statement = select(Button).offset(skip).limit(limit)
        buttons = session.exec(statement).all()
    else:
        # If not a superuser, filter Buttons by the current user's ID
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
    if not current_user.is_superuser and (button.created_by != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient permissions"
        )
    if not button:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Button not found"
        )
    usage_count = session.exec(
        select(func.count()).where(  # pylint: disable=E1102
            ButtonUse.button_id == button.id
        )
    ).one()

    return button


@router.post("/", response_model=ButtonPublic)
def create_button(
    *, session: SessionDep, current_user: CurrentUser, button_in: ButtonCreate
) -> Any:
    """
    Create a new Button.
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
    if not current_user.is_superuser and (button.created_by != current_user.id):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="Insufficient permissions"
        )
    if not button:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Button not found"
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
    force: bool = False,
) -> Message:
    """
    Delete a Button if requesting user has permission. Using the
    optional query parameter `force=true` will delete the Button
    even if it has usage history or is not retired.
    """
    button = session.get(Button, id)
    if not current_user.is_superuser and (button.created_by != current_user.id):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="Insufficient permissions"
        )
    if not button:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Button not found"
        )
    if button.retired_at is None:
        if not force:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Button must be retired before it can be deleted "
                    "(override with `force=true`)"
                ),
            )

    try:
        session.delete(button)
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        if not force:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Button can't be deleted because it has usage history. "
                    "Use `force=true` to override this and delete along with its history.",
                ),
            ) from exc
        # Force delete: remove related ButtonUse and ButtonRetirement entries first.
        session.exec(delete(ButtonUse).where(ButtonUse.button_id == button.id))
        session.exec(
            delete(ButtonRetirement).where(ButtonRetirement.button_id == button.id)
        )
        session.delete(button)
        session.commit()
    return Message(message="Button deleted successfully")


@router.get("/{id}/increment", response_model=ButtonPublic)
def increment_button_usage(
    request: Request,
    session: SessionDep,
    id: uuid.UUID,  # pylint: disable=redefined-builtin
) -> Any:
    """
    Increment the usage count of a Button.
    """
    # Uses using row-level locking

    statement = select(Button).where(Button.id == id).with_for_update()
    button = session.exec(statement).one_or_none()
    if not button:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Button not found")
    if button.retired_at is not None:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="Button is retired and cannot be incremented",
        )

    client_ip = get_client_ip(request)

    # Create a new ButtonUse entry
    button_use = ButtonUse(button_id=button.id, origin=client_ip)
    session.add(button_use)

    # Safely increment the usage count field using the locked row
    button.usage_count += 1

    session.commit()
    session.refresh(button)
    return button


@router.get("/{id}/usage")
def get_button_usage(
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,  # pylint: disable=redefined-builtin
) -> Any:
    """
    Get the usage count and recent uses of a Button.
    """
    button = session.get(Button, id)
    if not current_user.is_superuser and (button.created_by != current_user.id):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="Insufficient permissions"
        )
    if not button:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Button not found")
    usage_count = session.exec(
        select(func.count()).where(ButtonUse.button_id == id)  # pylint: disable=E1102
    ).one()
    recent_uses = session.exec(
        select(ButtonUse)
        .where(ButtonUse.button_id == id)
        .order_by(desc(ButtonUse.timestamp))
        .limit(10)
    ).all()
    return {
        "usage_count": usage_count,
        "recent_uses": [
            {"timestamp": use.timestamp, "origin": use.origin} for use in recent_uses
        ],
    }


@router.put("/{id}/retire", response_model=ButtonPublic)
def update_retirement(
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,  # pylint: disable=redefined-builtin
    retire_req: RetireButtonRequest,
) -> Any:
    """
    Retire or unretire a Button.
    """
    button = session.get(Button, id)
    if not button:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Button not found")
    if not current_user.is_superuser and button.created_by != current_user.id:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="Insufficient permissions"
        )

    if retire_req.retire is True:
        # Retire
        if button.retired_at is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Button is already retired",
            )
        now_utc = datetime.now(timezone.utc)
        button_retirement = ButtonRetirement(
            button_id=button.id, retired_at=now_utc, created_by=current_user.id
        )
        session.add(button_retirement)
        button.retired_at = now_utc

    elif retire_req.retire is False:
        # Unretire
        if button.retired_at is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Button is not currently retired",
            )
        stmt = (
            select(ButtonRetirement)
            .where(
                ButtonRetirement.button_id == button.id,
                ButtonRetirement.unretired_at.is_(None),  # pylint: disable=E1101
            )
            .order_by(desc(ButtonRetirement.retired_at))
        )
        button_retirement = session.exec(stmt).first()
        if not button_retirement:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No retirement record found for this Button",
            )
        button_retirement.unretired_at = datetime.now(timezone.utc)
        button.retired_at = None
        session.add(button_retirement)

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must specify retire=true or retire=false",
        )

    session.add(button)
    session.commit()
    session.refresh(button)
    return button


@router.get("/{id}/retirements", response_model=ButtonRetirementsPublic)
def get_retirements(
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,  # pylint: disable=redefined-builtin
) -> Any:
    """
    Get retirement records for a Button.
    """
    button = session.get(Button, id)
    if not current_user.is_superuser and (button.created_by != current_user.id):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="Insufficient permissions"
        )
    if not button:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Button not found")

    retirement_records = session.exec(
        select(ButtonRetirement).where(ButtonRetirement.button_id == id)
    ).all()

    return ButtonRetirementsPublic(
        data=retirement_records, count=len(retirement_records)
    )


@router.get("/retirements/", response_model=ButtonRetirementsPublic)
def list_all_retirements(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    List all retirement records for Buttons. Depending on the role of
    the user making the request, the response may include all Buttons or
    only those retired by the requesting user.
    """
    # TODO: add filtering, sorting, calculate usage count across all Buttons returned

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(  # pylint: disable=E1102
            ButtonRetirement
        )
        count = session.exec(count_statement).one()
        statement = select(ButtonRetirement).offset(skip).limit(limit)
        button_retirements = session.exec(statement).all()
    else:
        # If not a superuser, filter Buttons by the current user's ID
        count_statement = (
            select(func.count())  # pylint: disable=E1102
            .select_from(ButtonRetirement)
            .where(ButtonRetirement.created_by == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(ButtonRetirement)
            .where(ButtonRetirement.created_by == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        button_retirements = session.exec(statement).all()

    return ButtonRetirementsPublic(data=button_retirements, count=count)
