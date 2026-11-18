import pytest


class TestPatientEndpoints:
    def test_get_patient_profile_unauthorized(self, client):
        response = client.get("/api/v1/patients/me")
        assert response.status_code in (401, 403)

    def test_get_and_update_patient_profile(self, client):
        # 1. Register a new patient
        reg = client.post(
            "/api/v1/auth/register",
            json={
                "email": "profile_patient@example.com",
                "password": "password123",
            },
        )
        assert reg.status_code == 201

        # 2. Login to get token
        login = client.post(
            "/api/v1/auth/login",
            json={
                "email": "profile_patient@example.com",
                "password": "password123",
            },
        )
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Get profile
        get_res = client.get("/api/v1/patients/me", headers=headers)
        assert get_res.status_code == 200
        patient_data = get_res.json()
        assert "id" in patient_data
        assert "user_id" in patient_data
        assert patient_data["date_of_birth"] is None

        # 4. Update profile
        update_res = client.put(
            "/api/v1/patients/me",
            headers=headers,
            json={
                "date_of_birth": "1990-05-15",
                "sex": "female",
            },
        )
        assert update_res.status_code == 200
        updated = update_res.json()
        assert updated["date_of_birth"] == "1990-05-15"
        assert updated["sex"] == "female"
