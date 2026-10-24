import asyncio
import logging
from datetime import datetime, timezone

from fastapi import BackgroundTasks, FastAPI, Request, status
from pydantic import BaseModel, EmailStr, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address


# Send application logs to the console.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("notification-service")


# Apply rate limits based on the client's IP address.
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Background Notification Microservice",
    description="Accepts notification requests and processes them in the background.",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)


# Validate the incoming notification data.
class NotificationRequest(BaseModel):
    email: EmailStr
    subject: str = Field(min_length=1, max_length=150)
    message: str = Field(min_length=1, max_length=2000)


# Simulate an email notification in the background.
async def process_notification(notification: NotificationRequest):
    try:
        # Simulate work that takes two seconds.
        await asyncio.sleep(2)

        logger.info(
            "Background notification processed | recipient=%s | subject=%s | time=%s",
            notification.email,
            notification.subject,
            datetime.now(timezone.utc).isoformat(),
        )

        # A real email provider would send the message here.
        # This demo only logs that the notification was processed.

    except Exception:
        logger.exception("Background notification failed")


# Health check: confirms that the service is running.
@app.get("/")
async def health_check():
    return {
        "status": "healthy",
        "service": "notification-service",
    }


# Accept a notification and process it after returning the response.
@app.post(
    "/notifications",
    status_code=status.HTTP_202_ACCEPTED,
)
@limiter.limit("5/minute")
async def create_notification(
    request: Request,
    notification: NotificationRequest,
    background_tasks: BackgroundTasks,
):
    background_tasks.add_task(
        process_notification,
        notification,
    )

    return {
        "message": "Notification accepted for background processing",
        "recipient": notification.email,
        "status": "queued",
    }