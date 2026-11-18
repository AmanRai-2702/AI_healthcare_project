import pytest
from app.models.user import User
from app.models.doctor import Doctor
from app.core.security import hash_password


class TestDoctorEndpoints:
    def test_get_doctor_profile_unauthorized(self, client):
        response = client.get("/api/v1/doctors/me")
        assert response.status_code in (401, 403)

    def test_patient_cannot_access_doctor_routes(self, client):
        # Register as patient
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "not_doctor@example.com",
                "password": "password123",
            },
        )
        login = client.post(
            "/api/v1/auth/login",
            json={
                "email": "not_doctor@example.com",
                "password": "password123",
            },
        )
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Should be forbidden for patient role
        response = client.get("/api/v1/doctors/me", headers=headers)
        assert response.status_code == 403

    def test_doctor_profile_get_and_update(self, client, db_session):
        # Create doctor directly in DB
        doctor_user = User(
            email="dr.smith@hospital.org",
            password_hash=hash_password("docpassword123"),
            role="doctor",
        )
        db_session.add(doctor_user)
        db_session.flush()

        doc_profile = Doctor(
            user_id=doctor_user.id,
            specialization="Cardiology",
            license_number="LIC-12345",
            organization="General Hospital",
        )
        db_session.add(doc_profile)
        db_session.commit()

        # Login as doctor
        login = client.post(
            "/api/v1/auth/login",
            json={
                "email": "dr.smith@hospital.org",
                "password": "docpassword123",
            },
        )
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get doctor profile
        get_res = client.get("/api/v1/doctors/me", headers=headers)
        assert get_res.status_code == 200
        data = get_res.json()
        assert data["specialization"] == "Cardiology"
        assert data["license_number"] == "LIC-12345"
        assert data["organization"] == "General Hospital"

        # Update doctor profile
        put_res = client.put(
            "/api/v1/doctors/me",
            headers=headers,
            json={
                "specialization": "Interventional Cardiology",
                "license_number": "LIC-12345",
                "organization": "Heart Center",
            },
        )
        assert put_res.status_code == 200
        updated = put_res.json()
        assert updated["specialization"] == "Interventional Cardiology"
        assert updated["organization"] == "Heart Center"
