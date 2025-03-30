"""
Models for SQLAlchemy and Pydantic.
"""

import uuid
from datetime import datetime, timezone

from pydantic import EmailStr
from sqlalchemy import text
from sqlalchemy.orm import Mapped
from sqlmodel import Column, DateTime, Field, Relationship, SQLModel

# USER -----------------------------------------------------------------


class UserBase(SQLModel):
    """
    Shared User properties.
    """

    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


class UserCreate(UserBase):
    """
    Properties to receive via API on User creation.
    """

    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    """
    Properties to receive via API on registration.
    """

    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


class UserUpdate(UserBase):
    """
    Properties to receive via API on update, all are optional.
    """

    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    """
    For updating the current User.
    """

    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    """
    Properties to receive via API on password update.
    """

    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


class User(UserBase, table=True):
    """
    Database model, database table inferred from class name.
    """

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    buttons: Mapped[list["Button"]] = Relationship(
        back_populates="creator", cascade_delete=True
    )


class UserPublic(UserBase):
    """
    Properties to return via API, `id` is always required.
    """

    id: uuid.UUID


class UsersPublic(SQLModel):
    """
    Wrapper for a list of all users that includes a count.
    """

    data: list[UserPublic]
    count: int


# BUTTON ---------------------------------------------------------------


class ButtonBase(SQLModel):
    """
    Shared properties for all Button models.
    """

    type: str = Field(
        ..., max_length=50, description="Button type (e.g. PSA, ID, SFX)"
    )  # TODO: use enum values?
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    duration: float | None = Field(
        default=None, description="Seconds, if relevant for PSA/ID/SFX"
    )
    source: str | None = Field(default=None, max_length=255)


class ButtonCreate(ButtonBase):
    """
    Properties to receive on Button creation.
    """

    # 'created_by' derived from the logged-in user, so not accepted here


class ButtonUpdate(ButtonBase):
    """
    Properties to receive on Button update.
    """

    type: str | None = Field(default=None, max_length=50)
    title: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    duration: float | None = Field(default=None)
    source: str | None = Field(default=None, max_length=255)


class Button(ButtonBase, table=True):
    """
    Button database model, database table inferred from class name.
    """

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            server_default=text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            onupdate=text("CURRENT_TIMESTAMP"),
            server_default=text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )
    # Foreign key to user
    # Currently, if the user is deleted, the button will be deleted as
    # well (as well as all buttons created by that user)
    # TODO: set to a default "deleted" user instead?
    created_by: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    # Load the user who created the button, via the relationship:
    creator: Mapped["User"] = Relationship(back_populates="buttons")
    usage_count: int = Field(default=0)
    retired_at: datetime | None = Field(default=None)


class ButtonPublic(ButtonBase):
    """
    Button properties to return via API, `id` is always required.
    """

    id: uuid.UUID
    created_by: uuid.UUID
    usage_count: int
    retired_at: datetime | None


class ButtonsPublic(SQLModel):
    """
    Wrapper for a list of all buttons that includes a count.
    """

    data: list[ButtonPublic]
    count: int


# MESSAGE --------------------------------------------------------------


class Message(SQLModel):
    """
    Generic message used in endpoint responses.
    """

    message: str


# AUTH -----------------------------------------------------------------


class Token(SQLModel):
    """
    JSON payload containing access token.
    """

    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    """
    Contents of JWT token.
    """

    sub: str | None = None


class NewPassword(SQLModel):
    """
    Input string used for password resets.
    """

    token: str
    new_password: str = Field(min_length=8, max_length=40)
