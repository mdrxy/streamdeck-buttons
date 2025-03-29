"""
Tests for the buttons API endpoints.
"""

import uuid

from app.core.config import settings
from app.tests.utils.button import create_random_button
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session


def test_create_button(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """
    Test the creation of a new button.
    """
    data = {"title": "Foo", "description": "Fighters", "type": "PSA"}
    response = client.post(
        f"{settings.API_V1_STR}/buttons/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert "id" in content
    assert "created_by" in content


def test_read_button(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test the retrieval of a button by ID.
    """
    button = create_random_button(db)
    response = client.get(
        f"{settings.API_V1_STR}/buttons/{button.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert content["title"] == button.title
    assert content["description"] == button.description
    assert content["id"] == str(button.id)
    assert content["created_by"] == str(button.created_by)


def test_read_button_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """
    Test the retrieval of a button that does not exist.
    """
    response = client.get(
        f"{settings.API_V1_STR}/buttons/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    content = response.json()
    assert content["detail"] == "Button not found"


def test_read_button_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test the retrieval of a button with insufficient permissions.
    """
    button = create_random_button(db)
    response = client.get(
        f"{settings.API_V1_STR}/buttons/{button.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    content = response.json()
    assert content["detail"] == "Insufficient permissions"


def test_read_buttons(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test the retrieval of all buttons.
    """
    create_random_button(db)
    create_random_button(db)
    response = client.get(
        f"{settings.API_V1_STR}/buttons/",
        headers=superuser_token_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content["data"]) >= 2


def test_update_button(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test the update of a button.
    """
    button = create_random_button(db)
    data = {"title": "Updated title", "description": "Updated description"}
    response = client.put(
        f"{settings.API_V1_STR}/buttons/{button.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert content["id"] == str(button.id)
    assert content["created_by"] == str(button.created_by)


def test_update_button_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """
    Test the update of a button that does not exist.
    """
    data = {"title": "Updated title", "description": "Updated description"}
    response = client.put(
        f"{settings.API_V1_STR}/buttons/{uuid.uuid4()}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    content = response.json()
    assert content["detail"] == "Button not found"


def test_update_button_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test the update of a button with insufficient permissions.
    """
    button = create_random_button(db)
    data = {"title": "Updated title", "description": "Updated description"}
    response = client.put(
        f"{settings.API_V1_STR}/buttons/{button.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    content = response.json()
    assert content["detail"] == "Insufficient permissions"


def test_delete_button(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test the deletion of a button.
    """
    button = create_random_button(db)
    response = client.delete(
        f"{settings.API_V1_STR}/buttons/{button.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert content["message"] == "Button deleted successfully"


def test_delete_button_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """
    Test the deletion of a button that does not exist.
    """
    response = client.delete(
        f"{settings.API_V1_STR}/buttons/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    content = response.json()
    assert content["detail"] == "Button not found"


def test_delete_button_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test the deletion of a button with insufficient permissions.
    """
    button = create_random_button(db)
    response = client.delete(
        f"{settings.API_V1_STR}/buttons/{button.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    content = response.json()
    assert content["detail"] == "Insufficient permissions"
