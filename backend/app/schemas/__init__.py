from .auth import Token, TokenRefresh, LoginRequest
from .user import UserCreate, UserRead, UserUpdate, UserList
from .appointment import AppointmentCreate, AppointmentRead, AppointmentUpdate, AppointmentStatusUpdate, AppointmentList
from .doctor import DoctorProfileRead, DoctorProfileUpdate, DoctorSlot

__all__ = [
    "Token", "TokenRefresh", "LoginRequest",
    "UserCreate", "UserRead", "UserUpdate", "UserList",
    "AppointmentCreate", "AppointmentRead", "AppointmentUpdate",
    "AppointmentStatusUpdate", "AppointmentList",
    "DoctorProfileRead", "DoctorProfileUpdate", "DoctorSlot",
]
