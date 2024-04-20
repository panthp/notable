import pytest
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.main import app
from app.models import Base
from app.database import get_db
from contextlib import contextmanager

# Set up a test database
DATABASE_URL = "sqlite:///./notable.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Creates a new database session for a test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
async def client(db_session):
    """Uses the dependency override mechanism to replace the get_db dependency with a session that rolls back changes."""
    async def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

# Example test using the client and db_session fixtures
@pytest.mark.asyncio
async def test_create_and_get_doctors(client):
    response = await client.post("/doctors/", json={"first_name": "John", "last_name": "Doe"})
    assert response.status_code == 200
    response = await client.get("/doctors/")
    assert response.status_code == 200
    doctors_list = response.json()
    assert len(doctors_list) == 1
    assert doctors_list[0]['first_name'] == "John"
    assert doctors_list[0]['last_name'] == "Doe"

@pytest.mark.asyncio
async def test_delete_doctor(client):
    # First, create a doctor to delete
    create_resp = await client.post("/doctors/", json={"first_name": "John", "last_name": "Doe"})
    doctor_id = create_resp.json()['id']

    # Now, delete the doctor
    del_response = await client.delete(f"/doctors/{doctor_id}/")
    assert del_response.status_code == 204

    # # Verify the doctor has been deleted
    # verify_response = await client.get(f"/doctors/{doctor_id}/")
    # assert verify_response.status_code == 200
    # doctors = verify_response.json()
    # assert not any(doctor['id'] == doctor_id for doctor in doctors)

@pytest.mark.asyncio
async def test_appointment_operations(client):
    # Create a doctor
    doctor_resp = await client.post("/doctors/", json={"first_name": "John", "last_name": "Doe"})
    doctor_id = doctor_resp.json()['id']

    # Create an appointment for the doctor
    appointment_data = {"doctor_id": doctor_id, "patient_first_name": "Jane", "patient_last_name": "Smith", "date": "2024-04-20", "time": "08:15", "kind": "New Patient"}
    appt_response = await client.post("/appointments/", json=appointment_data)
    assert appt_response.status_code == 200
    appt_data = appt_response.json()
    assert appt_data['patient_first_name'] == "Jane"

    # Retrieve appointments for the doctor on the specified date
    get_appts_response = await client.get(f"/appointments/{doctor_id}/{appointment_data['date']}/")
    assert get_appts_response.status_code == 200
    appts_list = get_appts_response.json()
    assert len(appts_list) == 1
    assert appts_list[0]['time'] == "08:15"

    # Delete the appointment
    appt_id = appt_data['id']
    del_appt_response = await client.delete(f"/appointments/{appt_id}/")
    assert del_appt_response.status_code == 204

    # Verify the appointment has been deleted
    verify_appt_response = await client.get(f"/appointments/{doctor_id}/{appointment_data['date']}/")
    assert verify_appt_response.status_code == 200
    assert len(verify_appt_response.json()) == 0
