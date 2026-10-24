# Task 4: Background Tasks and Docker Microservice

## Project Description
A FastAPI microservice that accepts notification requests, processes simulated notifications in the background, applies rate limiting, and runs inside a Docker container.

## Features
- FastAPI REST endpoint for notifications
- Background processing with FastAPI BackgroundTasks
- Rate limiting of five requests per minute per client IP
- Email address and request data validation
- Application logging
- Health check endpoint
- Multi-stage Docker build
- Non-root container user

## Technologies
- Python 3.12
- FastAPI
- Uvicorn
- SlowAPI
- Docker

## Run with Docker
Build the image:

    docker build -t datheon-notification-service .

Start the container:

    docker run --name datheon-notifications -p 8000:8000 datheon-notification-service

Open the interactive API documentation:

    http://127.0.0.1:8000/docs

## Test a Notification
Send a POST request to `/notifications` with this JSON body:

    {
      "email": "student@example.com",
      "subject": "Task 4 test",
      "message": "Testing background notification processing."
    }

The API accepts the request and processes the simulated notification in the background. View the container logs to see when processing completes.

## Rate Limiting
The API allows five notification requests per minute per client IP. Additional requests during the limit window receive HTTP 429 Too Many Requests.

## Limitations
This is a learning demonstration. Notifications are simulated rather than sent through an actual email service. FastAPI BackgroundTasks is suitable for lightweight work, not durable jobs that must survive application crashes.
