# Notable Takehome Project

This project is a simple web backend built with FastAPI, using SQLAlchemy for ORM and SQLite as the database. It includes Docker support for containerization.

## Features

- Basic API endpoints (GET, POST, DELETE)
- SQLite database integration
- Dockerized application setup
- Data validation with Pydantic

## Prerequisites

Before you begin, ensure you have met the following requirements:
- Docker installed on your machine
- Basic knowledge of Python and FastAPI

## Installation

To set up this project, follow these steps:

1. Clone the repository: https://github.com/panthp/notable


2. Build the Docker container: docker build -t notable-takehome .


3. Run the Docker container: docker run -p 80:80 notable-takehome


## Usage

Once the application is running, you can access it at `http://localhost:80`.

### API Endpoints

## Doctors

- **POST /doctors/** - Add a new doctor
- **GET /doctors/** - Read all doctors
- **GET /doctors/{doctor_id}/** - Get a specific doctor
- **DELETE /doctors/{doctor_id}/** - Delete a doctor

### Appointments

- **GET /appointments/{doctor_id}/{appointment_date}/** - Read appointments for a doctor on a specific date
- **POST /appointments/** - Add a new appointment
- **DELETE /appointments/{appointment_id}/** - Delete an appointment

### Development

To modify and test the application locally without Docker:

1. Install the Python dependencies: pip install -r requirements.txt


## Usage

Once the application is running, you can access it at `http://localhost`.

### API Endpoints

- `GET /`: Returns a simple "Hello, World!" message.
- `GET /items/`: Fetches the first item from the database.

## Development

To modify and test the application locally without Docker:

1. Install the Python dependencies: pip install -r requirements.txt

2. Run the application using Uvicorn: uvicorn app.main:app --reload


This command will start the server on `http://localhost:8000`, where you can access the API and see changes in real-time.

## Contributing

Contributions to this project are welcome. To contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b new-feature`).
3. Make your changes and commit them (`git commit -am 'Add some feature'`).
4. Push to the branch (`git push origin new-feature`).
5. Open a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
