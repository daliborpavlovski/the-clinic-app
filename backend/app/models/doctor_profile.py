from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, ForeignKey, Text, JSON, DateTime
from sqlalchemy.orm import relationship
from ..database import Base


class DoctorProfile(Base):
    __tablename__ = "doctor_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    specialty = Column(String(200), nullable=False)
    bio = Column(Text, nullable=True)
    # Available slots: list of {"day": 0-6, "start": "09:00", "end": "17:00"}
    available_slots = Column(JSON, default=list)
    # Appointment duration in minutes
    slot_duration_minutes = Column(Integer, default=30)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="doctor_profile")
