"""Authentication API for the AI Book project with user background collection."""

from fastapi import APIRouter, HTTPException, Request
from typing import Optional
import logging
import re

from pydantic import BaseModel, validator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth")


class RegisterRequest(BaseModel):
    email: str
    password: str
    firstName: str
    lastName: str
    developerLevel: Optional[str] = "beginner"
    roboticsInterests: Optional[str] = ""
    preferredAiModel: Optional[str] = "openai"
    learningGoals: Optional[str] = ""
    programmingLanguages: Optional[str] = ""
    yearsExperience: Optional[int] = 0

    @validator('email')
    def validate_email(cls, v):
        if not v or "@" not in v:
            raise ValueError("Valid email is required")
        return v

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    @validator('firstName', 'lastName')
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("This field is required")
        return v


class LoginRequest(BaseModel):
    email: str
    password: str

    @validator('email')
    def validate_email(cls, v):
        if not v or "@" not in v:
            raise ValueError("Valid email is required")
        return v

    @validator('password')
    def validate_password(cls, v):
        if not v:
            raise ValueError("Password is required")
        return v


class ProfileUpdateRequest(BaseModel):
    developerLevel: Optional[str] = None
    roboticsInterests: Optional[str] = None
    preferredAiModel: Optional[str] = None
    learningGoals: Optional[str] = None
    programmingLanguages: Optional[str] = None
    yearsExperience: Optional[int] = None


@router.post("/register")
async def register_user(request: RegisterRequest):
    """Register a new user with comprehensive background information."""
    try:
        # Validate input data more thoroughly
        if not request.email or "@" not in request.email:
            raise HTTPException(status_code=400, detail="Valid email is required")

        if len(request.password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

        if len(request.password) > 128:  # Reasonable max length
            raise HTTPException(status_code=400, detail="Password is too long")

        if not request.firstName or not request.lastName:
            raise HTTPException(status_code=400, detail="First and last name are required")

        # Additional validation: check for common weak passwords
        weak_passwords = ["password", "12345678", "qwerty123"]
        if request.password.lower() in weak_passwords:
            raise HTTPException(status_code=400, detail="Password is too weak")

        # In a real implementation, this would integrate with Better Auth
        # and store the additional user data in custom fields
        user_data = {
            "id": f"user_{hash(request.email)}",  # Mock user ID
            "email": request.email,
            "firstName": request.firstName,
            "lastName": request.lastName,
            "developerLevel": request.developerLevel,
            "roboticsInterests": request.roboticsInterests,
            "preferredAiModel": request.preferredAiModel,
            "learningGoals": request.learningGoals,
            "programmingLanguages": request.programmingLanguages,
            "yearsExperience": request.yearsExperience,
            "createdAt": "2023-01-01T00:00:00Z",
            "profileComplete": True
        }

        logger.info(f"User registered with background info: {request.email}")
        return {"success": True, "user": user_data}
    except HTTPException:
        raise
    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")


@router.post("/login")
async def login_user(request: LoginRequest):
    """Authenticate user and return session token."""
    try:
        # Validate input data
        if not request.email or "@" not in request.email:
            raise HTTPException(status_code=400, detail="Valid email is required")

        if not request.password:
            raise HTTPException(status_code=400, detail="Password is required")

        # Additional validation for email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, request.email):
            raise HTTPException(status_code=400, detail="Invalid email format")

        # Mock session data
        session_data = {
            "userId": f"user_{hash(request.email)}",
            "email": request.email,
            "expiresAt": "2023-01-02T00:00:00Z",
        }

        logger.info(f"User logged in: {request.email}")
        return {"success": True, "session": session_data}
    except HTTPException:
        raise
    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")


@router.post("/profile/update")
async def update_profile(request: ProfileUpdateRequest, req: Request):
    """Update user profile with comprehensive background information."""
    try:
        # In a real implementation, this would update the user in the Better Auth database
        # Collect only non-None values for update
        update_data = {}
        for field, value in request.dict().items():
            if value is not None:
                update_data[field] = value

        updated_profile = {
            # Include any existing profile data here in a real implementation
            **update_data
        }

        logger.info(f"Profile updated with background info")
        return {"success": True, "profile": updated_profile}
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        raise HTTPException(status_code=500, detail="Profile update failed")


@router.get("/profile")
async def get_profile(req: Request):
    """Get user profile information with background details."""
    try:
        # In a real implementation, this would fetch user data from Better Auth
        # including the custom fields for background info
        profile_data = {
            "developerLevel": "intermediate",
            "roboticsInterests": "Humanoid robotics, AI planning",
            "preferredAiModel": "openai",
            "learningGoals": "Learn advanced robotics concepts",
            "programmingLanguages": "Python, C++, JavaScript",
            "yearsExperience": 3,
        }

        return {"success": True, "profile": profile_data}
    except Exception as e:
        logger.error(f"Profile fetch error: {e}")
        raise HTTPException(status_code=500, detail="Profile fetch failed")


@router.post("/collect-background")
async def collect_user_background(request: RegisterRequest):
    """Additional endpoint to collect and update user background information."""
    try:
        background_data = {
            "developerLevel": request.developerLevel,
            "roboticsInterests": request.roboticsInterests,
            "preferredAiModel": request.preferredAiModel,
            "learningGoals": request.learningGoals,
            "programmingLanguages": request.programmingLanguages,
            "yearsExperience": request.yearsExperience,
        }

        logger.info(f"Background information collected for user: {request.email}")
        return {"success": True, "data": background_data}
    except Exception as e:
        logger.error(f"Background collection error: {e}")
        raise HTTPException(status_code=500, detail="Background collection failed")