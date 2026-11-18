import pytest
from app.models.user import User
from app.core.security import hash_password


class TestPermissions:
    def test_role_based_access_patient(self, client):
        # Register a patient
        client.post(
            "/api/v1/auth/register",
            json={"email": "perm_patient@example.com", "password": "password123"},
        )
        login = client.post(
            "/api/v1/auth/login",
            json={"email": "perm_patient@example.com", "password": "password123"},
        )
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Patient can access patient routes
        res = client.get("/api/v1/patients/me", headers=headers)
        assert res.status_code == 200

        # Patient CANNOT access doctor routes
        res_doc = client.get("/api/v1/doctors/me", headers=headers)
        assert res_doc.status_code == 403

    def test_inactive_user_is_blocked(self, client, db_session):
        # Create an inactive user
        user = User(
            email="inactive@example.com",
            password_hash=hash_password("password123"),
            role="patient",
            is_active=False,
        )
        db_session.add(user)
        db_session.commit()

        # Login will fail because authenticate_user checks is_active
        login = client.post(
            "/api/v1/auth/login",
            json={"email": "inactive@example.com", "password": "password123"},
        )
        assert login.status_code == 401
