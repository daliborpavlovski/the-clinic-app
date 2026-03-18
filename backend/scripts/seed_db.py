#!/usr/bin/env python3
"""
Seed The Clinic App database with initial users and sample data.
Run: python -m scripts.seed_db  (from /backend directory)
"""
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import SessionLocal, engine
from app.models import User, UserRole, Appointment, AppointmentStatus, DoctorProfile
from app.services.auth_service import AuthService

ADMIN_EMAIL = "admin@theclinicapp.com"
DOCTOR_EMAIL = "doctor@theclinicapp.com"
PATIENT_EMAIL = "patient@theclinicapp.com"

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin1234!")
DOCTOR_PASSWORD = os.getenv("DOCTOR_PASSWORD", "Doctor1234!")
PATIENT_PASSWORD = os.getenv("PATIENT_PASSWORD", "Patient1234!")


def seed():
    db = SessionLocal()
    auth = AuthService(db)

    print("Seeding database...")

    # --- Users ---
    admin = db.query(User).filter(User.email == ADMIN_EMAIL).first()
    if not admin:
        admin = User(
            email=ADMIN_EMAIL,
            hashed_password=auth.hash_password(ADMIN_PASSWORD),
            full_name="Admin User",
            role=UserRole.admin,
        )
        db.add(admin)
        print(f"  Created admin: {ADMIN_EMAIL}")
    else:
        print(f"  Admin already exists: {ADMIN_EMAIL}")

    doctor = db.query(User).filter(User.email == DOCTOR_EMAIL).first()
    if not doctor:
        doctor = User(
            email=DOCTOR_EMAIL,
            hashed_password=auth.hash_password(DOCTOR_PASSWORD),
            full_name="Dr. Sarah Mitchell",
            role=UserRole.doctor,
        )
        db.add(doctor)
        print(f"  Created doctor: {DOCTOR_EMAIL}")
    else:
        print(f"  Doctor already exists: {DOCTOR_EMAIL}")

    patient = db.query(User).filter(User.email == PATIENT_EMAIL).first()
    if not patient:
        patient = User(
            email=PATIENT_EMAIL,
            hashed_password=auth.hash_password(PATIENT_PASSWORD),
            full_name="John Patient",
            role=UserRole.patient,
        )
        db.add(patient)
        print(f"  Created patient: {PATIENT_EMAIL}")
    else:
        print(f"  Patient already exists: {PATIENT_EMAIL}")

    db.commit()
    db.refresh(admin)
    db.refresh(doctor)
    db.refresh(patient)

    # --- Doctor Profile ---
    profile = db.query(DoctorProfile).filter(DoctorProfile.user_id == doctor.id).first()
    if not profile:
        profile = DoctorProfile(
            user_id=doctor.id,
            specialty="General Practice",
            bio="Dr. Sarah Mitchell is a board-certified general practitioner with 10 years of experience.",
            available_slots=[
                {"day": 0, "start": "09:00", "end": "17:00"},  # Monday
                {"day": 1, "start": "09:00", "end": "17:00"},  # Tuesday
                {"day": 2, "start": "09:00", "end": "17:00"},  # Wednesday
                {"day": 3, "start": "09:00", "end": "17:00"},  # Thursday
                {"day": 4, "start": "09:00", "end": "13:00"},  # Friday (half day)
            ],
            slot_duration_minutes=30,
        )
        db.add(profile)
        db.commit()
        print("  Created doctor profile")

    # --- Sample Appointments ---
    appt_count = db.query(Appointment).count()
    if appt_count == 0:
        now = datetime.now(timezone.utc)

        appointments = [
            Appointment(
                patient_id=patient.id,
                doctor_id=doctor.id,
                start_time=now + timedelta(days=2, hours=2),
                end_time=now + timedelta(days=2, hours=2, minutes=30),
                status=AppointmentStatus.pending,
                reason="Annual checkup",
            ),
            Appointment(
                patient_id=patient.id,
                doctor_id=doctor.id,
                start_time=now + timedelta(days=5, hours=4),
                end_time=now + timedelta(days=5, hours=4, minutes=30),
                status=AppointmentStatus.confirmed,
                reason="Follow-up consultation",
                notes="Patient to bring previous test results",
            ),
            Appointment(
                patient_id=patient.id,
                doctor_id=doctor.id,
                start_time=now - timedelta(days=10),
                end_time=now - timedelta(days=10) + timedelta(minutes=30),
                status=AppointmentStatus.completed,
                reason="Routine blood work review",
                notes="All results normal. Next checkup in 6 months.",
            ),
        ]
        for appt in appointments:
            db.add(appt)
        db.commit()
        print(f"  Created {len(appointments)} sample appointments")

    print("\nSeed complete!")
    print(f"\n  Admin:   {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
    print(f"  Doctor:  {DOCTOR_EMAIL} / {DOCTOR_PASSWORD}")
    print(f"  Patient: {PATIENT_EMAIL} / {PATIENT_PASSWORD}")
    db.close()


if __name__ == "__main__":
    seed()
