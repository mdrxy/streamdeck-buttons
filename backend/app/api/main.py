"""
Main API router for the application.
"""

from app.api.routes import buttons, login, private, users, utils
from app.core.config import settings
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(buttons.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
