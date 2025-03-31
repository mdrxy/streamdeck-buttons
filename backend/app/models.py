"""
Models for SQLAlchemy and Pydantic.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr
from sqlalchemy import Column, ForeignKey, text
from sqlalchemy.orm import Mapped
from sqlmodel import DateTime, Field, Relationship, SQLModel

DEFAULT_DELETED_USER_ID: uuid.UUID = uuid.UUID("00000000-0000-0000-0000-000000000000")

# USER -----------------------------------------------------------------


class UserBase(SQLModel):  # pylint: disable=missing-class-docstring
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: Optional[str] = Field(default=None, max_length=255)


class UserCreate(UserBase):  # pylint: disable=missing-class-docstring
    # Properties to receive via API on User creation.
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):  # pylint: disable=missing-class-docstring
    # Properties to receive via API on registration.
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: Optional[str] = Field(default=None, max_length=255)


class UserUpdate(UserBase):  # pylint: disable=missing-class-docstring
    # Properties to receive via API on update, all are optional.
    email: Optional[EmailStr] = Field(default=None, max_length=255)  # type: ignore
    password: Optional[str] = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):  # pylint: disable=missing-class-docstring
    full_name: Optional[str] = Field(default=None, max_length=255)
    email: Optional[EmailStr] = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):  # pylint: disable=missing-class-docstring
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


class User(UserBase, table=True):  # pylint: disable=missing-class-docstring
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    buttons: Mapped[list["Button"]] = Relationship(back_populates="creator")


class UserPublic(UserBase):  # pylint: disable=missing-class-docstring
    id: uuid.UUID


class UsersPublic(SQLModel):  # pylint: disable=missing-class-docstring
    data: list[UserPublic]
    count: int


# BUTTON ---------------------------------------------------------------


class ButtonUse(SQLModel, table=True):  # pylint: disable=missing-class-docstring
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    button_id: uuid.UUID = Field(
        sa_column=Column(
            "button_id", ForeignKey("button.id", ondelete="CASCADE"), nullable=False
        )
    )
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    origin: Optional[str] = Field(default=None, max_length=255)
    button: Mapped["Button"] = Relationship(back_populates="uses")


class ButtonBase(SQLModel):  # pylint: disable=missing-class-docstring
    # Shared fields for ALL Button models.
    title: str = Field(min_length=1, max_length=255)
    type: str = Field(..., max_length=50, description="Button type (e.g. PSA, ID, SFX)")
    description: Optional[str] = Field(default=None, max_length=255)
    duration: Optional[int] = Field(default=None, description="In seconds")
    source: Optional[str] = Field(default=None, max_length=255)


class ButtonCreate(ButtonBase):  # pylint: disable=missing-class-docstring
    # (We don't accept 'id' or 'created_by' here; they're set automatically.)
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "description": "A hug is a great way to show you care.",
                "duration": 30,
                "source": "International Hug Day",
                "title": "Give Someone a Hug",
                "type": "PSA",
            }
        }
    )


class ButtonUpdate(ButtonBase):  # pylint: disable=missing-class-docstring
    # All fields are optional here, unlike creation.
    type: Optional[str] = Field(default=None, max_length=50)
    title: Optional[str] = Field(default=None, max_length=255)
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "PSA",
                "title": "Give Someone a Hug (Updated)",
                "description": "A hug is a great way to show you care. Updated for 2025.",
                "duration": 45,
                "source": "International Hug Day",
            }
        }
    )


class Button(ButtonBase, table=True):  # pylint: disable=missing-class-docstring
    # Actual SQLModel table that includes DB-specific fields. This class
    # won't typically have its own JSON example, since it's not the
    # direct input or output model.
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
    # Currently, if the user is deleted, the button will be deleted as
    # well (as well as all buttons created by that user)
    # TODO: set to a default "deleted" user instead?
    created_by: uuid.UUID = Field(
        sa_column=Column(
            "created_by",
            ForeignKey("user.id", ondelete="SET DEFAULT"),
            default=DEFAULT_DELETED_USER_ID,
            server_default=text("'00000000-0000-0000-0000-000000000000'::uuid"),
            nullable=False,
        )
    )
    # Load the user who created the button, via the relationship:
    creator: Mapped["User"] = Relationship(back_populates="buttons")
    retired_at: Optional[datetime] = Field(default=None)
    usage_count: int = Field(default=0, nullable=False)
    uses: Mapped[list[ButtonUse]] = Relationship(
        back_populates="button",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class ButtonPublic(ButtonBase):  # pylint: disable=missing-class-docstring
    # Fields returned when reading an existing button
    # Matches the final shape the API will return.
    id: uuid.UUID
    created_by: uuid.UUID
    usage_count: int
    retired_at: Optional[datetime]
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "aa557cdd-cc28-449a-8669-c4f2d331b4d9",
                "created_by": "5c6e110d-75e9-4ed7-b16c-6cc2435901a6",
                "type": "PSA",
                "title": "Give Someone a Hug",
                "description": "A hug is a great way to show you care.",
                "duration": 30,
                "source": "International Hug Day",
                "retired_at": "2025-03-31T12:34:56Z",
                "usage_count": 5,
            }
        }
    )


class ButtonsPublic(SQLModel):  # pylint: disable=missing-class-docstring
    data: list[ButtonPublic]
    count: int
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "data": [
                    {
                        "id": "aa557cdd-cc28-449a-8669-c4f2d331b4d9",
                        "created_by": "5c6e110d-75e9-4ed7-b16c-6cc2435901a6",
                        "type": "PSA",
                        "title": "Give Someone a Hug",
                        "description": "A hug is a great way to show you care.",
                        "duration": 30,
                        "source": "International Hug Day",
                        "retired_at": "2025-03-31T12:34:56Z",
                    },
                    {
                        "id": "bb337cdd-cc28-449a-8669-c4f2d331b500",
                        "created_by": "5c6e110d-75e9-4ed7-b16c-6cc2435901a6",
                        "type": "PSA",
                        "title": "Take a Deep Breath",
                        "description": "Relax for better health.",
                        "duration": 20,
                        "source": "Mindful Moments",
                        "retired_at": "2025-03-31T12:34:56Z",
                    },
                ],
                "count": 2,
            }
        }
    )


class ButtonRetirement(SQLModel, table=True):  # pylint: disable=missing-class-docstring
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    button_id: uuid.UUID = Field(
        foreign_key="button.id", nullable=False, ondelete="CASCADE"
    )
    created_by: uuid.UUID = Field(
        sa_column=Column(
            "created_by",
            ForeignKey("user.id", ondelete="SET DEFAULT"),
            default=DEFAULT_DELETED_USER_ID,
            server_default=text("'00000000-0000-0000-0000-000000000000'::uuid"),
            nullable=False,
        )
    )
    retired_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    unretired_at: Optional[datetime] = Field(default=None)
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "6a7da618-d3f8-4e40-af35-268a2a67dcf3",
                "button_id": "aa557cdd-cc28-449a-8669-c4f2d331b4d9",
                "created_by": "5c6e110d-75e9-4ed7-b16c-6cc2435901a6",
                "retired_at": "2025-03-31T12:34:56Z",
                "unretired_at": None,
            }
        }
    )


class RetireButtonRequest(BaseModel):
    """
    Request model for retiring a Button.
    """

    retire: bool | None = None


class ButtonRetirementsPublic(BaseModel):
    """
    Response model for Button retirement records.
    """

    data: list[ButtonRetirement]
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

    sub: Optional[str] = None


class NewPassword(SQLModel):
    """
    Input string used for password resets.
    """

    token: str
    new_password: str = Field(min_length=8, max_length=40)
