# Task 3: Database Persistence with SQLAlchemy and SQLite

## Project Description
This project is a REST API built with FastAPI, SQLAlchemy, and SQLite. It stores users and their notes persistently, even after the server restarts.

## Features
- User registration and login
- JWT authentication
- Password hashing
- Asynchronous SQLAlchemy database sessions
- SQLite database persistence
- One-to-many relationship between users and notes
- Create, read, update, and delete notes
- Note ownership checks
- Pydantic request validation
- Interactive Swagger documentation

## Technologies
- Python 3
- FastAPI
- SQLAlchemy
- SQLite
- aiosqlite
- Pydantic
- python-jose
- Passlib and bcrypt

## Project Files
- `main.py`: API endpoints and authentication
- `database.py`: Database engine and session dependency
- `models.py`: User and Note database models
- `schemas.py`: Request and response schemas
- `requirements.txt`: Project dependencies

## Installation
Create and activate a virtual environment, then install the dependencies:

    python -m venv .venv
    .venv\Scripts\activate
    python -m pip install -r requirements.txt

Set the JWT_SECRET_KEY environment variable in your terminal before starting the application.

## Run the API

    uvicorn main:app --reload

Open http://127.0.0.1:8000/docs to test the endpoints.

## Database Persistence
The application creates an `app.db` SQLite database file automatically. User accounts and notes are stored in this database and remain available after the server restarts.

## Security
Passwords are stored as hashes, not plain text. JWT authentication protects private endpoints, and users can access only their own notes.

## Limitations
This is a learning project. It uses a local SQLite database and does not include production deployment configuration or database migrations.
