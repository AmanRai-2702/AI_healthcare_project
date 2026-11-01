# from uuid import UUID

# from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
# from sqlalchemy.orm import Session

# from app.core.security import decode_access_token
# from app.db.session import get_db
# from app.models.user import User


# oauth2_scheme = OAuth2PasswordBearer(
#     tokenUrl="/api/v1/auth/login"
# )


# def get_current_user(
#     token: str = Depends(oauth2_scheme),
#     db: Session = Depends(get_db),
# ) -> User:

#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials.",
#         headers={"WWW-Authenticate": "Bearer"},
#     )

#     try:
#         user_id: UUID = decode_access_token(token)
#     except Exception:
#         raise credentials_exception

#     user = db.get(User, user_id)

#     if user is None:
#         raise credentials_exception

#     if not user.is_active:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Your account is inactive.",
#         )

#     return user


# def require_roles(*allowed_roles: str):

#     def role_checker(
#         current_user: User = Depends(get_current_user),
#     ) -> User:

#         if current_user.role not in allowed_roles:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="You do not have permission to access this resource.",
#             )

#         return current_user

#     return role_checker



from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User
from uuid import UUID
from sqlalchemy import select
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.doctor_patient import DoctorPatient

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        user_id: UUID = decode_access_token(credentials.credentials)
    except Exception:
        raise credentials_exception

    user = db.get(User, user_id)

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is inactive.",
        )

    return user


def require_roles(*allowed_roles: str):

    def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:

        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource.",
            )

        return current_user

    return role_checker


def get_current_patient(
    current_user: User = Depends(require_roles("patient")),
    db: Session = Depends(get_db),
) -> Patient:

    patient = db.query(Patient).filter(
        Patient.user_id == current_user.id
    ).first()

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found.",
        )

    return patient

def get_current_doctor(
    current_user: User = Depends(require_roles("doctor")),
    db: Session = Depends(get_db),
) -> Doctor:

    doctor = db.scalar(
        select(Doctor).where(
            Doctor.user_id == current_user.id
        )
    )

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found.",
        )

    return doctor

def verify_doctor_patient_access(
    patient_id: UUID,
    current_doctor: Doctor = Depends(get_current_doctor),
    db: Session = Depends(get_db),
) -> Patient:

    patient = db.scalar(
        select(Patient)
        .join(
            DoctorPatient,
            DoctorPatient.patient_id == Patient.id,
        )
        .where(
            DoctorPatient.doctor_id == current_doctor.id,
            DoctorPatient.patient_id == patient_id,
            DoctorPatient.status == "active",
        )
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found or access not authorized.",
        )

    return patient



def get_patient_for_current_user(
    patient_id: UUID,
    current_user: User = Depends(require_roles("patient")),
    db: Session = Depends(get_db),
) -> Patient:

    patient = db.scalar(
        select(Patient).where(
            Patient.id == patient_id,
            Patient.user_id == current_user.id,
        )
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found.",
        )

    return patient


def get_current_hospital_admin(
    current_user: User = Depends(
        require_roles("hospital_admin")
    ),
) -> User:

    return current_user