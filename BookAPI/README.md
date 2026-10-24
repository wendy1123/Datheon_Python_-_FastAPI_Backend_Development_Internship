
# Book Management API

## Project Description

This project is a RESTful API built with Python, FastAPI, and Pydantic.
It allows users to create, view, search, update, and delete books.

## Features

- Create a new book
- View all books
- Retrieve a book by ID
- Filter books by title or author
- Update an existing book
- Delete a book
- Validate incoming book data
- Handle missing book IDs with appropriate HTTP errors
- Interactive API documentation using Swagger UI

## Technologies Used

- Python 3
- FastAPI
- Pydantic
- Uvicorn

## Installation

1. Install Python 3.
2. Open a terminal in the project folder.
3. Create a virtual environment:

   python -m venv .venv

4. Activate the virtual environment on Windows:

   .venv\Scripts\activate

5. Install the dependencies:

   python -m pip install -r requirements.txt

## Run the Application

uvicorn main:app --reload

## API Documentation

Open the following address in your browser after starting the server:

http://127.0.0.1:8000/docs

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /books | List and filter books |
| GET | /books/{book_id} | Get one book |
| POST | /books | Create a book |
| PUT | /books/{book_id} | Update a book |
| DELETE | /books/{book_id} | Delete a book |

## Storage

This demonstration uses in-memory storage.
Books are reset when the application restarts.
