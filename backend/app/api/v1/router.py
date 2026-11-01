# from fastapi import APIRouter

# from app.api.v1.endpoints import (
#     health,
#     auth,
#     patients,
#     doctors,
#     doctor_patients,
# )

# api_router.include_router(doctor_patients.router)


# api_router = APIRouter()

# api_router.include_router(health.router)
# api_router.include_router(auth.router)
# api_router.include_router(patients.router)
# api_router.include_router(doctors.router)



from fastapi import APIRouter

from app.api.v1.endpoints import (
    health,
    auth,
    patients,
    doctors,
    doctor_patients,
)

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(patients.router)
api_router.include_router(doctors.router)
api_router.include_router(doctor_patients.router)