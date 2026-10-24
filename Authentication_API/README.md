
# User Authentication and RBAC API

## Project Description

This project is a REST API built with Python and FastAPI. It supports
user registration, login, JWT authentication, and role-based access control.

## Features

- User registration
- Password hashing with Passlib and bcrypt
- Login using username and password
- Signed JWT access tokens
- Token expiration
- Protected user profile endpoint
- Admin-only endpoint
- Request validation and error handling
- Interactive Swagger documentation

## Technologies

- Python 3
- FastAPI
- Uvicorn
- Pydantic
- python-jose
- Passlib
- bcrypt

## Installation

Create and activate a virtual environment, then install dependencies:

    python -m venv .venv
    .venv\Scripts\activate
    python -m pip install -r requirements.txt

## Configure Environment Variables

Set a private JWT signing key and demo admin credentials in your terminal
before starting the application.

Never publish real secrets or passwords.

## Run the API

    uvicorn main:app --reload

Open the interactive API documentation:

http://127.0.0.1:8000/docs

## Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /register | Register a normal user |
| POST | /login | Log in and receive a JWT |
| GET | /users/me | View the authenticated user's profile |
| GET | /admin/dashboard | View admin-only information |

## Storage and Limitations

This learning project stores users in memory, so registered users are
lost when the application restarts. A production system should use a
persistent database and additional security controls.
