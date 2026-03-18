from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..dependencies import get_db, get_current_user
from ..models.appointment import Appointment, AppointmentStatus
from ..models.user import User, UserRole
from ..schemas.appointment import (
    AppointmentCreate, AppointmentRead, AppointmentUpdate,
    AppointmentStatusUpdate, AppointmentList,
)
from ..services.appointment_service import AppointmentService
from ..utils.exceptions import not_found, forbidden
from ..utils.pagination import Pagination

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post("", response_model=AppointmentRead, status_code=status.HTTP_201_CREATED)
def create_appointment(
    payload: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == UserRole.doctor:
        from ..utils.exceptions import forbidden
        raise forbidden("Doctors cannot book appointments as patients")
    service = AppointmentService(db)
    return service.create_appointment(payload, current_user)


@router.get("", response_model=AppointmentList)
def list_appointments(
    pagination: Pagination = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Appointment)

    if current_user.role == UserRole.patient:
        query = query.filter(Appointment.patient_id == current_user.id)
    elif current_user.role == UserRole.doctor:
        query = query.filter(Appointment.doctor_id == current_user.id)
    # admin sees all

    total = query.count()
    items = query.order_by(Appointment.start_time.desc()).offset(pagination.offset).limit(pagination.size).all()
    return {
        "items": items,
        **pagination.paginate(total),
    }


@router.get("/{appointment_id}", response_model=AppointmentRead)
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AppointmentService(db)
    return service.get_appointment_for_user(appointment_id, current_user)


@router.put("/{appointment_id}", response_model=AppointmentRead)
def update_appointment(
    appointment_id: int,
    payload: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AppointmentService(db)
    appointment = service.get_appointment_for_user(appointment_id, current_user)

    if payload.notes is not None:
        appointment.notes = payload.notes
    if payload.reason is not None:
        appointment.reason = payload.reason

    db.commit()
    db.refresh(appointment)
    return appointment


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise not_found("Appointment")

    # Only the patient who booked it or an admin can delete
    if current_user.role == UserRole.patient and appointment.patient_id != current_user.id:
        raise forbidden("You can only delete your own appointments")
    if current_user.role == UserRole.doctor:
        raise forbidden("Doctors cannot delete appointments")

    db.delete(appointment)
    db.commit()
    return None


@router.patch("/{appointment_id}/status", response_model=AppointmentRead)
def update_appointment_status(
    appointment_id: int,
    payload: AppointmentStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise not_found("Appointment")

    # Access control: patient can cancel their own, doctor can confirm/complete theirs, admin can do anything
    if current_user.role == UserRole.patient:
        if appointment.patient_id != current_user.id:
            raise forbidden("You can only update your own appointments")
        if payload.status != AppointmentStatus.cancelled:
            raise forbidden("Patients can only cancel appointments")
    elif current_user.role == UserRole.doctor:
        if appointment.doctor_id != current_user.id:
            raise forbidden("You can only update appointments assigned to you")

    service = AppointmentService(db)
    return service.transition_status(appointment, payload.status, current_user)
