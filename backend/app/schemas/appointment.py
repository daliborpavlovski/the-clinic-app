from datetime import datetime
from pydantic import BaseModel
from ..models.appointment import AppointmentStatus


class AppointmentCreate(BaseModel):
    doctor_id: int
    start_time: datetime
    end_time: datetime
    reason: str | None = None


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
