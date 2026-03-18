from datetime import datetime
from pydantic import BaseModel, Field, model_validator
from ..models.appointment import AppointmentStatus


class AppointmentCreate(BaseModel):
    doctor_id: int
    start_time: datetime
    end_time: datetime
    reason: str | None = Field(default=None, max_length=500)

    @model_validator(mode='after')
    def end_must_be_after_start(self) -> 'AppointmentCreate':
        if self.end_time <= self.start_time:
            raise ValueError('end_time must be after start_time')
        return self


class AppointmentRead(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    start_time: datetime
    end_time: datetime
    status: AppointmentStatus
    reason: str | None
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AppointmentUpdate(BaseModel):
    notes: str | None = None
    reason: str | None = None


class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus


class AppointmentList(BaseModel):
    items: list[AppointmentRead]
    total: int
    page: int
    size: int
    pages: int
