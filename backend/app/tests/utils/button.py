"""
This module contains utility functions for creating random button
instances for testing purposes.
"""

import random

from app import crud
from app.models import Button, ButtonCreate
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string
from sqlmodel import Session


def create_random_button(db: Session) -> Button:
    """
    Generate a random button instance.
    """
    user = create_random_user(db)
    owner_id = user.id
    assert owner_id is not None
    title = random_lower_string()
    description = random_lower_string()
    button_type = random.choice(["PSA", "ID", "SFX"])
    button_in = ButtonCreate(title=title, description=description, type=button_type)
    return crud.create_button(session=db, button_in=button_in, created_by=owner_id)
