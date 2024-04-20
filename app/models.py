from sqlalchemy import Column, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.sqlite import VARCHAR
import uuid
from app.database import Base
from app.schemas import AppointmentKind

class Doctor(Base):
    __tablename__ = 'doctors'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = Column(String)
    last_name = Column(String)
    appointments = relationship("Appointment", back_populates="doctor")  # relationship definition

class Appointment(Base):
    __tablename__ = 'appointments'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    doctor_id = Column(String, ForeignKey('doctors.id'))  # ForeignKey reference
    doctor = relationship("Doctor", back_populates="appointments")  # relationship definition
    patient_first_name = Column(String)
    patient_last_name = Column(String)
    date = Column(String)
    time = Column(String)
    kind = Column(Enum(AppointmentKind))
