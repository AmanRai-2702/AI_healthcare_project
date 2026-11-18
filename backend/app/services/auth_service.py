from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.patient import Patient
from app.schemas.user import UserCreate
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)


def register_patient(db: Session, user_data: UserCreate) -> User:
    """Register a new patient account."""

    # Prevent public registration with privileged roles.
    if user_data.role != "patient":
        raise ValueError(
            "Public registration is only available for patients."
        )

    # Check whether email already exists.
    existing_user = db.scalar(
        select(User).where(User.email == user_data.email)
    )

    if existing_user:
        raise ValueError("An account with this email already exists.")

    # Create user account.
    new_user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role="patient",
    )

    db.add(new_user)
    db.flush()

    # Automatically create the associated patient profile.
    patient_profile = Patient(user_id=new_user.id)

    db.add(patient_profile)

    try:
        db.commit()
        db.refresh(new_user)
        return new_user

    except Exception:
        db.rollback()
        raise


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> tuple[User, str] | None:
    """Authenticate a user and generate an access token."""

    user = db.scalar(
        select(User).where(User.email == email)
    )

    if not user:
        return None

    if not user.is_active:
        return None

    if not verify_password(password, user.password_hash):
        return None

    access_token = create_access_token(user.id)

    return user, access_token