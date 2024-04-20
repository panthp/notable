from enum import Enum
from pydantic import BaseModel, validator
from datetime import datetime

class DoctorCreate(BaseModel):
    first_name: str
    last_name: str

class Doctor(BaseModel):
    id: str # UUID4
    first_name: str
    last_name: str

    class Config:
        orm_mode = True

class AppointmentKind(str, Enum):
    new_patient = "New Patient"
    follow_up = "Follow-up"

class AppointmentBase(BaseModel):
    doctor_id: str  # UUID4
    patient_first_name: str
    patient_last_name: str
    date: str  # YYYY-MM-DD
    time: str  # HH:MM
    kind: AppointmentKind

    @validator('time')
    def validate_time(cls, v):
        try:
            # Convert string to time object
            time_obj = datetime.strptime(v, '%H:%M')
            # Check if the minutes are a multiple of 15
            if time_obj.minute % 15 != 0:
                raise ValueError('Time must be in 15-minute increments')
        except ValueError as e:
            raise ValueError(f"Invalid time format or value: {e}")
        return v

class AppointmentCreate(AppointmentBase):
    pass

class Appointment(AppointmentBase):
    id: str # UUID4

    class Config:
        orm_mode = True
