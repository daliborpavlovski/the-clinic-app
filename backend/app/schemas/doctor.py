from datetime import datetime
from pydantic import BaseModel


class DoctorSlotAvailability(BaseModel):
    day: int  # 0=Monday, 6=Sunday
    start: str  # "09:00"
    end: str  # "17:00"


class DoctorProfileRead(BaseModel):
    id: int
    user_id: int
    specialty: str
    bio: str | None
    available_slots: list[DoctorSlotAvailability]
    slot_duration_minutes: int
    doctor_name: str | None = None
    doctor_email: str | None = None

    model_config = {"from_attributes": True}


class DoctorProfileUpdate(BaseModel):
    specialty: str | None = None
    bio: str | None = None
    available_slots: list[DoctorSlotAvailability] | None = None
    slot_duration_minutes: int | None = None


class DoctorSlot(BaseModel):
    start_time: datetime
    end_time: datetime
    available: bool
