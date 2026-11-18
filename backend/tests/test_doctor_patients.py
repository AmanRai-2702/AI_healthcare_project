import pytest
from app.models.user import User
from app.models.doctor import Doctor
from app.core.security import hash_password


class TestDoctorPatientEndpoints:
    def test_doctor_patient_request_lifecycle(self, client, db_session):
        # 1. Create a doctor
        doc_user = User(
            email="dr.access@hospital.org",
            password_hash=hash_password("docpassword123"),
            role="doctor",
        )
        db_session.add(doc_user)
        db_session.flush()

        doctor = Doctor(
            user_id=doc_user.id,
            specialization="Neurology",
            license_number="LIC-9999",
            organization="Metro Health",
        )
        db_session.add(doctor)
        db_session.commit()

        # Doctor login
        doc_login = client.post(
            "/api/v1/auth/login",
            json={"email": "dr.access@hospital.org", "password": "docpassword123"},
        )
        doc_token = doc_login.json()["access_token"]
        doc_headers = {"Authorization": f"Bearer {doc_token}"}

        # 2. Register a patient
        patient_reg = client.post(
            "/api/v1/auth/register",
            json={"email": "patient_access@example.com", "password": "patientpwd123"},
        )
        assert patient_reg.status_code == 201

        # Patient login
        patient_login = client.post(
            "/api/v1/auth/login",
            json={"email": "patient_access@example.com", "password": "patientpwd123"},
        )
        patient_token = patient_login.json()["access_token"]
        patient_headers = {"Authorization": f"Bearer {patient_token}"}

        # Get patient profile to get patient ID
        p_profile = client.get("/api/v1/patients/me", headers=patient_headers).json()
        patient_id = p_profile["id"]

        # 3. Doctor requests access to patient
        req_res = client.post(
            "/api/v1/doctors/me/patient-requests",
            headers=doc_headers,
            json={"patient_id": patient_id},
        )
        assert req_res.status_code == 201
        rel_data = req_res.json()
        assert rel_data["status"] == "pending"
        rel_id = rel_data["id"]

        # 4. Patient lists incoming doctor requests
        list_res = client.get(
            "/api/v1/patients/me/doctor-requests",
            headers=patient_headers,
        )
        assert list_res.status_code == 200
        p_requests = list_res.json()
        assert p_requests["total"] >= 1
        assert any(r["id"] == rel_id for r in p_requests["relationships"])

        # 5. Patient approves request
        approve_res = client.put(
            f"/api/v1/patients/me/doctor-requests/{rel_id}",
            headers=patient_headers,
            json={"status": "active"},
        )
        assert approve_res.status_code == 200
        assert approve_res.json()["status"] == "active"
        assert approve_res.json()["granted_at"] is not None

        # 6. Doctor lists their active patients
        doc_patients_res = client.get(
            "/api/v1/doctors/me/patients",
            headers=doc_headers,
        )
        assert doc_patients_res.status_code == 200
        doc_patients = doc_patients_res.json()
        assert doc_patients["total"] >= 1
