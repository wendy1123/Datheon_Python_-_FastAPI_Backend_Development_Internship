
import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field



app = FastAPI(
    title="User Authentication API",
    description="Registration, login, JWT authentication, and RBAC.",
    version="1.0.0",
)




SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "Set the JWT_SECRET_KEY environment variable before starting the API."
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30



password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")




users = {}



class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=72)



class UserPublic(BaseModel):
    username: str
    role: str



class TokenResponse(BaseModel):
    access_token: str
    token_type: str



def create_access_token(username: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": username,
        "exp": expires_at,
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)



def create_demo_admin():
    username = os.getenv("DEMO_ADMIN_USERNAME")
    password = os.getenv("DEMO_ADMIN_PASSWORD")

    if username and password:
        if len(password) < 8 or len(password) > 72:
            raise RuntimeError(
                "Demo admin password must contain 8 to 72 bytes."
            )

        users[username] = {
            "username": username,
            "password_hash": password_context.hash(password),
            "role": "admin",
        }


create_demo_admin()



@app.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
)
def register(user: UserRegister):
    if user.username in users:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )

    users[user.username] = {
        "username": user.username,
        "password_hash": password_context.hash(user.password),
        "role": "user",
    }

    return {
        "username": user.username,
        "role": "user",
    }



@app.post("/login", response_model=TokenResponse)
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    user = users.get(form.username)

    if (
        user is None
        or not password_context.verify(
            form.password,
            user["password_hash"],
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(user["username"])

    return {
        "access_token": token,
        "token_type": "bearer",
    }



def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
):
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

    user = users.get(username)

    if user is None:
        raise credentials_error

    return user



def require_admin(
    current_user: Annotated[dict, Depends(get_current_user)],
):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required",
        )

    return current_user



@app.get("/")
def home():
    return {"message": "Authentication API is running"}



@app.get("/users/me", response_model=UserPublic)
def read_my_profile(
    current_user: Annotated[dict, Depends(get_current_user)],
):
    return {
        "username": current_user["username"],
        "role": current_user["role"],
    }



@app.get("/admin/dashboard", response_model=UserPublic)
def admin_dashboard(
    admin: Annotated[dict, Depends(require_admin)],
):
    return {
        "username": admin["username"],
        "role": admin["role"],
    }
