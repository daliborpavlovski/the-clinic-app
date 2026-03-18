import re
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, model_validator

_TIME_RE = re.compile(r'^(?:[01]\d|2[0-3]):[0-5]\d$')


class DoctorSlotAvailability(BaseModel):
    day: int = Field(..., ge=0, le=6)  # 0=Monday, 6=Sunday
    start: str  # "09:00"
    end: str  # "17:00"

    @field_validator('start', 'end')
    @classmethod
    def validate_time_format(cls, v: str) -> str:
        if not _TIME_RE.match(v):
            raise ValueError('Time must be in HH:MM format (24-hour)')
        return v

    @model_validator(mode='after')
    def end_must_be_after_start(self) -> 'DoctorSlotAvailability':
        if self.start >= self.end:
            raise ValueError('end time must be after start time')
        return self


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
