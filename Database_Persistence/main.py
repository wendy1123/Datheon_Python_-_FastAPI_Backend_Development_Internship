import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Query,
    Response,
    status,
)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import Base, engine, get_db
from models import Note, User
from schemas import (
    NoteCreate,
    NotePublic,
    NoteUpdate,
    TokenResponse,
    UserPublic,
    UserRegister,
)


# Set this environment variable before starting the API.
SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError(
        "Set the JWT_SECRET_KEY environment variable before starting the API."
    )

ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30

password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# Create the database tables when the application starts.
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


app = FastAPI(
    title="Persistent Notes API",
    description="A FastAPI project using SQLAlchemy, SQLite, and JWT.",
    version="1.0.0",
    lifespan=lifespan,
)


# Create a signed JWT access token.
def create_access_token(username: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": username,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


# Find the currently authenticated user.
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired access token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        username = payload.get("sub")

        if not username:
            raise credentials_error

    except JWTError:
        raise credentials_error

    result = await db.execute(
        select(User).where(User.username == username)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_error

    return user


# Home endpoint.
@app.get("/")
async def home():
    return {
        "message": "Persistent Notes API is running",
        "docs": "/docs",
    }


# Register a new user.
@app.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_data: UserRegister,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(User).where(User.username == user_data.username)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )

    new_user = User(
        username=user_data.username,
        password_hash=password_context.hash(user_data.password),
        role="user",
    )

    db.add(new_user)

    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not create this user. Check whether the username exists.",
        )

    await db.refresh(new_user)
    return new_user


# Log in and receive a JWT token.
@app.post("/login", response_model=TokenResponse)
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(User).where(User.username == form.username)
    )
    user = result.scalar_one_or_none()

    if (
        user is None
        or not password_context.verify(
            form.password,
            user.password_hash,
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(user.username)

    return {
        "access_token": token,
        "token_type": "bearer",
    }


# View the profile of the logged-in user.
@app.get("/users/me", response_model=UserPublic)
async def read_my_profile(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user


# Create a note belonging to the logged-in user.
@app.post(
    "/notes",
    response_model=NotePublic,
    status_code=status.HTTP_201_CREATED,
)
async def create_note(
    note_data: NoteCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    note = Note(
        title=note_data.title,
        content=note_data.content,
        owner_id=current_user.id,
    )

    db.add(note)
    await db.commit()
    await db.refresh(note)

    return note


# Get only the logged-in user's notes.
# An optional title parameter filters the results.
@app.get("/notes", response_model=list[NotePublic])
async def get_notes(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    title: str | None = Query(default=None),
):
    query = select(Note).where(Note.owner_id == current_user.id)

    if title:
        query = query.where(Note.title.ilike(f"%{title}%"))

    result = await db.execute(query)
    return result.scalars().all()


# Get one note, provided it belongs to the logged-in user.
@app.get("/notes/{note_id}", response_model=NotePublic)
async def get_note(
    note_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(Note).where(
            Note.id == note_id,
            Note.owner_id == current_user.id,
        )
    )
    note = result.scalar_one_or_none()

    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    return note


# Update a note belonging to the logged-in user.
@app.put("/notes/{note_id}", response_model=NotePublic)
async def update_note(
    note_id: int,
    note_data: NoteUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(Note).where(
            Note.id == note_id,
            Note.owner_id == current_user.id,
        )
    )
    note = result.scalar_one_or_none()

    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    note.title = note_data.title
    note.content = note_data.content

    await db.commit()
    await db.refresh(note)

    return note


# Delete a note belonging to the logged-in user.
@app.delete(
    "/notes/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_note(
    note_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(Note).where(
            Note.id == note_id,
            Note.owner_id == current_user.id,
        )
    )
    note = result.scalar_one_or_none()

    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    await db.delete(note)
    await db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)