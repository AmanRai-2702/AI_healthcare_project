from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.schemas.user import UserCreate
from app.api.deps import get_current_user
from app.models.user import User

from app.db.session import get_db
from app.services.auth_service import (
    register_patient,
    authenticate_user,
)
from app.schemas.auth import (
    PatientRegistrationRequest,
    LoginRequest,
    RegistrationResponse,
    LoginResponse,
    AuthUserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user_data: PatientRegistrationRequest,
    db: Session = Depends(get_db),
):
    try:
        registration_data = UserCreate(
            email=user_data.email,
        password=user_data.password,
        role="patient",
        )
        user = register_patient(db, registration_data)

        return RegistrationResponse(
            message="Patient account created successfully.",
            user=AuthUserResponse.model_validate(user),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )


@router.post(
    "/login",
    response_model=LoginResponse,
)
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db),
):
    result = authenticate_user(
        db,
        credentials.email,
        credentials.password,
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user, access_token = result

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=AuthUserResponse.model_validate(user),
    )
    
@router.get("/me", response_model=AuthUserResponse)
def get_my_account(
    current_user: User = Depends(get_current_user),
):
    return current_user