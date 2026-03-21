from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from ..models.appointment import Appointment, AppointmentStatus, STATUS_TRANSITIONS
from ..models.user import User, UserRole
from ..schemas.appointment import AppointmentCreate
from ..utils.exceptions import bad_request, conflict, forbidden, not_found


class AppointmentService:
    def __init__(self, db: Session):
        self.db = db

    def create_appointment(self, data: AppointmentCreate, patient: User) -> Appointment:
        now = datetime.now(timezone.utc)

        # Must be in the future
        start = data.start_time
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        end = data.end_time
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)

        if start <= now:
            raise bad_request("Appointment must be scheduled for a future time slot")

        # Check double-booking for patient
        patient_conflict = self._check_conflict(None, start, end, patient.id)
        if patient_conflict:
            raise conflict("You already have an appointment at this time slot")

        # Check double-booking for doctor
        doctor_conflict = self._check_conflict(data.doctor_id, start, end, None)
        if doctor_conflict:
            raise conflict("Doctor is not available at this time slot")

        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=data.doctor_id,
            start_time=start,
            end_time=end,
            reason=data.reason,
            status=AppointmentStatus.pending,
        )
        self.db.add(appointment)
        self.db.commit()
        self.db.refresh(appointment)
        return appointment

    def _check_conflict(
        self, check_doctor_id: int | None, start: datetime, end: datetime,
        check_patient_id: int | None, exclude_id: int | None = None
    ) -> bool:
        query = self.db.query(Appointment).filter(
            Appointment.status.in_([AppointmentStatus.pending, AppointmentStatus.confirmed]),
            Appointment.start_time < end,
            Appointment.end_time > start,
        )
        if exclude_id:
            query = query.filter(Appointment.id != exclude_id)

        if check_doctor_id:
            query = query.filter(Appointment.doctor_id == check_doctor_id)
        if check_patient_id:
            query = query.filter(Appointment.patient_id == check_patient_id)

        return query.first() is not None

    def transition_status(
        self, appointment: Appointment, new_status: AppointmentStatus, current_user: User
    ) -> Appointment:
        # Validate transition
        allowed = STATUS_TRANSITIONS.get(appointment.status, [])
        if new_status not in allowed:
            raise bad_request(
                f"Cannot transition from '{appointment.status}' to '{new_status}'. "
                f"Allowed transitions: {[s.value for s in allowed]}"
            )

        # Cancel within 1 hour restriction
        if new_status == AppointmentStatus.cancelled:
            now = datetime.now(timezone.utc)
            start = appointment.start_time
            if start.tzinfo is None:
                start = start.replace(tzinfo=timezone.utc)
            if start - now < timedelta(hours=1):
                raise bad_request("Cannot cancel appointment within 1 hour of start time")

        appointment.status = new_status
        appointment.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(appointment)
        return appointment

    def get_appointment_for_user(self, appointment_id: int, current_user: User) -> Appointment:
        appointment = self.db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise not_found("Appointment")
        # Patients can only see their own appointments
        if current_user.role == UserRole.patient and appointment.patient_id != current_user.id:
            raise forbidden("You can only access your own appointments")
        return appointment
