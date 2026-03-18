from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..dependencies import get_db, get_current_user
from ..models.user import User, UserRole
from ..models.doctor_profile import DoctorProfile
from ..models.appointment import Appointment, AppointmentStatus
from ..schemas.doctor import DoctorProfileRead, DoctorProfileUpdate, DoctorSlot
from ..utils.exceptions import not_found, forbidden
from ..utils.pagination import Pagination

router = APIRouter(prefix="/doctors", tags=["doctors"])


def _profile_to_read(profile: DoctorProfile) -> DoctorProfileRead:
    return DoctorProfileRead(
        id=profile.id,
        user_id=profile.user_id,
        specialty=profile.specialty,
        bio=profile.bio,
        available_slots=profile.available_slots or [],
        slot_duration_minutes=profile.slot_duration_minutes,
        doctor_name=profile.user.full_name if profile.user else None,
        doctor_email=profile.user.email if profile.user else None,
    )


@router.get("", response_model=dict)
def list_doctors(
    pagination: Pagination = Depends(),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = db.query(DoctorProfile)
    total = query.count()
    profiles = query.offset(pagination.offset).limit(pagination.size).all()
    return {
        "items": [_profile_to_read(p) for p in profiles],
        **pagination.paginate(total),
    }


@router.get("/{doctor_id}", response_model=DoctorProfileRead)
def get_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    profile = db.query(DoctorProfile).filter(DoctorProfile.user_id == doctor_id).first()
    if not profile:
        raise not_found("Doctor profile")
    return _profile_to_read(profile)


@router.get("/{doctor_id}/slots", response_model=list[DoctorSlot])
def get_doctor_slots(
    doctor_id: int,
    from_date: datetime = Query(default=None),
    to_date: datetime = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    profile = db.query(DoctorProfile).filter(DoctorProfile.user_id == doctor_id).first()
    if not profile:
        raise not_found("Doctor profile")

    now = datetime.now(timezone.utc)
    start = from_date or now
    end = to_date or (now + timedelta(days=7))

    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)

    # Get booked appointments
    booked = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.status.in_([AppointmentStatus.pending, AppointmentStatus.confirmed]),
        Appointment.start_time >= start,
        Appointment.end_time <= end,
    ).all()
    booked_times = {(a.start_time, a.end_time) for a in booked}

    slots: list[DoctorSlot] = []
    duration = timedelta(minutes=profile.slot_duration_minutes)
    available_days = {s["day"]: s for s in (profile.available_slots or [])}

    current = start.replace(minute=0, second=0, microsecond=0)
    while current < end:
        weekday = current.weekday()
        if weekday in available_days:
            day_cfg = available_days[weekday]
            day_start_h, day_start_m = map(int, day_cfg["start"].split(":"))
            day_end_h, day_end_m = map(int, day_cfg["end"].split(":"))

            slot_start = current.replace(hour=day_start_h, minute=day_start_m)
            day_end = current.replace(hour=day_end_h, minute=day_end_m)

            while slot_start + duration <= day_end:
                slot_end = slot_start + duration
                if slot_start >= now:
                    is_available = (slot_start, slot_end) not in booked_times
                    slots.append(DoctorSlot(
                        start_time=slot_start,
                        end_time=slot_end,
                        available=is_available,
                    ))
                slot_start = slot_end

        current += timedelta(days=1)
        current = current.replace(hour=0, minute=0, second=0, microsecond=0)

    return slots


@router.put("/{doctor_id}/profile", response_model=DoctorProfileRead)
def update_doctor_profile(
    doctor_id: int,
    payload: DoctorProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Doctors can only edit their own profile; admins can edit any
    if current_user.role == UserRole.doctor and current_user.id != doctor_id:
        raise forbidden("Doctors can only edit their own profile")
    if current_user.role == UserRole.patient:
        raise forbidden("Patients cannot edit doctor profiles")

    profile = db.query(DoctorProfile).filter(DoctorProfile.user_id == doctor_id).first()
    if not profile:
        raise not_found("Doctor profile")

    if payload.specialty is not None:
        profile.specialty = payload.specialty
    if payload.bio is not None:
        profile.bio = payload.bio
    if payload.available_slots is not None:
        profile.available_slots = [s.model_dump() for s in payload.available_slots]
    if payload.slot_duration_minutes is not None:
        profile.slot_duration_minutes = payload.slot_duration_minutes

    db.commit()
    db.refresh(profile)
    return _profile_to_read(profile)
