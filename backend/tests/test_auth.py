import pytest


class TestAuthEndpoints:
    def test_register_patient_success(self, client):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "patient@example.com",
                "password": "strongpassword123",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "user" in data
        assert data["user"]["email"] == "patient@example.com"
        assert data["user"]["role"] == "patient"
        assert "id" in data["user"]

    def test_register_duplicate_email(self, client):
        # First registration
        res1 = client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "strongpassword123",
            },
        )
        assert res1.status_code == 201

        # Second registration with same email
        res2 = client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "anotherpassword123",
            },
        )
        assert res2.status_code == 409

    def test_login_valid_credentials(self, client):
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "login_test@example.com",
                "password": "password123",
            },
        )

        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "login_test@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "login_test@example.com"

    def test_login_invalid_password(self, client):
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "wrong_pwd@example.com",
                "password": "correctpassword123",
            },
        )

        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "wrong_pwd@example.com",
                "password": "incorrectpassword",
            },
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "ghost@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == 401

    def test_get_my_account(self, client):
        reg = client.post(
            "/api/v1/auth/register",
            json={
                "email": "me@example.com",
                "password": "password123",
            },
        )
        assert reg.status_code == 201

        login = client.post(
            "/api/v1/auth/login",
            json={
                "email": "me@example.com",
                "password": "password123",
            },
        )
        token = login.json()["access_token"]

        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json()["email"] == "me@example.com"

    def test_get_my_account_unauthorized(self, client):
        response = client.get("/api/v1/auth/me")
        assert response.status_code in (401, 403)
