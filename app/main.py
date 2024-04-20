import logging
from fastapi import FastAPI, HTTPException, Depends, Response, status
from sqlalchemy.orm import Session
from app import models, schemas, database
from app.database import SessionLocal, engine, get_db

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/doctors/", response_model=schemas.Doctor)
def add_doctor(doctor: schemas.DoctorCreate, db: Session = Depends(get_db)):
    # Log the information about adding a new doctor
    logging.info("Adding a new doctor: %s %s", doctor.first_name, doctor.last_name)
    try:
        # Create a new instance of the Doctor model with the provided data
        db_doctor = models.Doctor(first_name=doctor.first_name, last_name=doctor.last_name)
        # Add the doctor to the database session
        db.add(db_doctor)
        # Commit the changes to the database
        db.commit()
        # Refresh the doctor object to get the updated values from the database
        db.refresh(db_doctor)
        # Log the successful addition of the doctor
        logging.info("Doctor added successfully with ID: %s", db_doctor.id)
        # Return the added doctor as the response
        return db_doctor
    except Exception as e:
        # Log the error if there is any exception during the process
        logging.error("Error adding doctor: %s", str(e))
        # Raise an HTTPException with a 500 status code and the error message as the detail
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/doctors/", response_model=list[schemas.Doctor])
def read_doctors(db: Session = Depends(get_db)):
    # Log the information about fetching all doctors
    logging.info("Fetching all doctors")
    try:
        # Query the database to get all doctors
        doctors = db.query(models.Doctor).all()
        if not doctors: 
            # Log a message if no doctors are found
            logging.info("No doctors found")
        else:
            # Log the successful fetching of doctors with the count
            logging.info("Doctors fetched successfully with count: %d", len(doctors))
        # Return the fetched doctors as the response
        return doctors
    except Exception as e:
        # Log the error if there is any exception during the process
        logging.error("Error fetching doctors: %s", str(e))
        # Raise an HTTPException with a 500 status code and the error message as the detail
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.get("/doctors/{doctor_id}/", response_model=schemas.Doctor)
def get_doctor(doctor_id: str, db: Session = Depends(get_db)):
    # Log the information about fetching a specific doctor
    logging.info("Fetching doctor with ID: %s", doctor_id)
    try:
        # Query the database to get the doctor with the provided ID
        db_doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
        if db_doctor is None:
            # Log a warning if the doctor is not found
            logging.warning("Doctor not found with ID: %s", doctor_id)
            # Raise an HTTPException with a 404 status code and a "Doctor not found" detail
            raise HTTPException(status_code=404, detail="Doctor not found")
        # Log the successful fetching of the doctor
        logging.info("Doctor fetched successfully")
        # Return the fetched doctor as the response
        return db_doctor
    except Exception as e:
        # Log the error if there is any exception during the process
        logging.error("Error fetching doctor: %s", str(e))
        # Raise an HTTPException with a 500 status code and the error message as the detail
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.delete("/doctors/{doctor_id}/", status_code=204)
def delete_doctor(doctor_id: str, db: Session = Depends(get_db)):
    # Log the information about deleting a doctor
    logging.info("Attempting to delete doctor with ID: %s", doctor_id)
    # Fetch the doctor to see if they exist
    db_doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not db_doctor:
        # Log a warning if the doctor is not found for deletion
        logging.warning("Doctor not found for deletion with ID: %s", doctor_id)
        # Raise an HTTPException with a 404 status code and a "Doctor not found" detail
        raise HTTPException(status_code=404, detail="Doctor not found")

    # Try to delete the doctor and handle database errors separately
    try:
        # Delete the doctor from the database
        db.delete(db_doctor)
        # Commit the changes to the database
        db.commit()
        # Log the successful deletion of the doctor
        logging.info("Doctor deleted successfully")
    except Exception as e:
        # Log the error if there is any exception during the process
        logging.error("Error deleting doctor: %s", str(e))
        # Rollback the session to ensure data consistency
        db.rollback()
        # Raise an HTTPException with a 500 status code and a generic error message
        raise HTTPException(status_code=500, detail="Internal server error") from e

    # Return a response with a 204 status code (No Content)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.get("/appointments/{doctor_id}/{appointment_date}/", response_model=list[schemas.Appointment])
def read_appointments(doctor_id: str, appointment_date: str, db: Session = Depends(get_db)):
    # Log the information about fetching appointments for a specific doctor on a specific date
    logging.info("Fetching appointments for doctor ID %s on date %s", doctor_id, appointment_date)
    try:
        # Query the database to get the appointments for the specified doctor and date
        appointments = db.query(models.Appointment).filter(
            models.Appointment.doctor_id == doctor_id,
            models.Appointment.date == appointment_date
        ).all()
        # Log the successful fetching of appointments
        logging.info("Appointments fetched successfully")
        # Return the fetched appointments as the response
        return appointments
    except Exception as e:
        # Log the error if there is any exception during the process
        logging.error("Error fetching appointments: %s", str(e))
        # Raise an HTTPException with a 500 status code and the error message as the detail
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.post("/appointments/", response_model=schemas.Appointment)
def add_appointment(appointment: schemas.AppointmentCreate, db: Session = Depends(get_db)):
    # Log the information about adding a new appointment
    logging.info("Adding new appointment for doctor ID %s", appointment.doctor_id)
    try:
        # Check if there are already 3 appointments at the same time slot for the given doctor
        existing_appointments = db.query(models.Appointment).filter(
            models.Appointment.doctor_id == appointment.doctor_id,
            models.Appointment.date == appointment.date,
            models.Appointment.time == appointment.time
        ).count()
        if existing_appointments >= 3:
            # Log an error if the appointment limit is exceeded
            logging.error("Attempt to exceed appointment limit at the same time slot")
            # Raise an HTTPException with a 400 status code and a specific error message
            raise HTTPException(status_code=400, detail="No more than 3 appointments can be added at the same time slot for a given doctor.")
        # Create a new instance of the Appointment model with the provided data
        new_appointment = models.Appointment(**appointment.dict())
        # Add the appointment to the database session
        db.add(new_appointment)
        # Commit the changes to the database
        db.commit()
        # Refresh the appointment object to get the updated values from the database
        db.refresh(new_appointment)
        # Log the successful addition of the appointment
        logging.info("Appointment added successfully")
        # Return the added appointment as the response
        return new_appointment
    except Exception as e:
        # Log the error if there is any exception during the process
        logging.error("Error adding appointment: %s", str(e))
        # Raise an HTTPException with a 500 status code and the error message as the detail
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/appointments/{appointment_id}/")
def delete_appointment(appointment_id: str, db: Session = Depends(get_db)):
    # Log the information about deleting an appointment
    logging.info("Deleting appointment with ID: %s", appointment_id)
    try:
        # Query the database to get the appointment with the provided ID
        appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
        if not appointment:
            # Log a warning if the appointment is not found for deletion
            logging.warning("Appointment not found for deletion with ID: %s", appointment_id)
            # Raise an HTTPException with a 404 status code and an "Appointment not found" detail
            raise HTTPException(status_code=404, detail="Appointment not found")
        # Delete the appointment from the database
        db.delete(appointment)
        # Commit the changes to the database
        db.commit()
        # Log the successful deletion of the appointment
        logging.info("Appointment deleted successfully")
        # Return a response with a 204 status code (No Content)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        # Log the error if there is any exception during the process
        logging.error("Error deleting appointment: %s", str(e))
        # Raise an HTTPException with a 500 status code and the error message as the detail
        raise HTTPException(status_code=500, detail=str(e))
