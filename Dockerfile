# Use official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /code

# Install any needed packages specified in requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application's code
COPY ./app /code/app

# Run the app. CMD specifies what command to run within the container.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]