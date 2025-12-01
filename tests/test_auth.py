import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

TOKEN_URL = "/api/token/"
TOKEN_REFRESH_URL = "/api/token/refresh/"


@pytest.mark.django_db
def test_obtain_token_success(api_client):
    User.objects.create_user(username="authuser", password="secret123")
    response = api_client.post(
        TOKEN_URL,
        {"username": "authuser", "password": "secret123"},
        format="json",
    )
    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_obtain_token_wrong_credentials(api_client):
    User.objects.create_user(username="authuser", password="secret123")
    response = api_client.post(
        TOKEN_URL,
        {"username": "authuser", "password": "wrong"},
        format="json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_refresh_token_success(api_client):
    user = User.objects.create_user(username="authuser", password="secret123")
    obtain = api_client.post(
        TOKEN_URL,
        {"username": "authuser", "password": "secret123"},
        format="json",
    )
    refresh = obtain.data["refresh"]

    response = api_client.post(
        TOKEN_REFRESH_URL,
        {"refresh": refresh},
        format="json",
    )
    assert response.status_code == 200
    assert "access" in response.data


@pytest.mark.django_db
def test_refresh_token_invalid(api_client):
    response = api_client.post(
        TOKEN_REFRESH_URL,
        {"refresh": "invalid-token"},
        format="json",
    )
    assert response.status_code in (400, 401)
