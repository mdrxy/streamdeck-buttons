"""
Utility routes for testing and health checks.
"""

from app.api.deps import get_current_active_superuser
from app.models import Message
from app.utils import generate_test_email, send_email
from fastapi import APIRouter, Depends, status
from pydantic.networks import EmailStr

router = APIRouter(prefix="/utils", tags=["utils"])


@router.post(
    "/test-email/",
    dependencies=[Depends(get_current_active_superuser)],
    status_code=status.HTTP_201_CREATED,
)
def test_email(email_to: EmailStr) -> Message:
    """
    Test emails by generating a test email and sending it to the
    specified address (superuser only).
    """
    email_data = generate_test_email(email_to=email_to)
    send_email(
        email_to=email_to,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message="Test email sent")


@router.get("/health-check/")
async def health_check() -> bool:
    """
    Simple health check endpoint to verify that the API is running.
    Used by monitoring tools.
    """
    return True
