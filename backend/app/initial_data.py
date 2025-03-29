"""
Script to create initial data in the database.
"""

import logging

from app.core.db import engine, init_db
from sqlmodel import Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    """
    Initialize the database with the first superuser.
    """
    with Session(engine) as session:
        init_db(session)


def main() -> None:
    """
    Entry point of the script.
    """
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
