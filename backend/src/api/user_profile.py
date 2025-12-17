"""User profile API for the AI Book project with Better Auth integration considerations."""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Optional
import logging

from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/users")


class UserProfileUpdateRequest(BaseModel):
    developerLevel: Optional[str] = None
    roboticsInterests: Optional[str] = None
    preferredAiModel: Optional[str] = None
    learningGoals: Optional[str] = None
    programmingLanguages: Optional[str] = None
    yearsExperience: Optional[int] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None


@router.get("/profile/{user_id}")
async def get_user_profile(user_id: str):
    """Get user profile information with background details."""
    try:
        # In a real implementation, this would fetch user data from a database
        # For now, we'll return mock data to simulate Better Auth integration
        profile_data = {
            "id": user_id,
            "email": "user@example.com",  # This would come from authentication
            "firstName": "John",
            "lastName": "Doe",
            "developerLevel": "intermediate",
            "roboticsInterests": "Humanoid robotics, AI planning",
            "preferredAiModel": "openai",
            "learningGoals": "Learn advanced robotics concepts",
            "programmingLanguages": "Python, C++, JavaScript",
            "yearsExperience": 3,
        }

        # In a real implementation, you'd fetch from your user database
        # where Better Auth user IDs are linked to additional profile data
        logger.info(f"Profile fetched for user: {user_id}")
        return {"success": True, "profile": profile_data}
    except Exception as e:
        logger.error(f"Profile fetch error: {e}")
        raise HTTPException(status_code=500, detail="Profile fetch failed")


@router.put("/profile/{user_id}")
async def update_user_profile(user_id: str, request: UserProfileUpdateRequest):
    """Update user profile with comprehensive background information."""
    try:
        # In a real implementation, this would update user data in a database
        # that's linked to the Better Auth user ID
        update_data = request.dict(exclude_unset=True)
        
        # Simulate updating user profile in database
        updated_profile = {
            "id": user_id,
            "developerLevel": update_data.get("developerLevel", "beginner"),
            "roboticsInterests": update_data.get("roboticsInterests", ""),
            "preferredAiModel": update_data.get("preferredAiModel", "openai"),
            "learningGoals": update_data.get("learningGoals", ""),
            "programmingLanguages": update_data.get("programmingLanguages", ""),
            "yearsExperience": update_data.get("yearsExperience", 0),
            "firstName": update_data.get("firstName", ""),
            "lastName": update_data.get("lastName", ""),
        }

        logger.info(f"Profile updated for user: {user_id}")
        return {"success": True, "profile": updated_profile}
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        raise HTTPException(status_code=500, detail="Profile update failed")


@router.post("/link-better-auth")
async def link_better_auth_user(request: Request):
    """Endpoint to link Better Auth user with additional profile data."""
    try:
        # This would be called when a Better Auth session is established
        # to link the Better Auth user ID with profile data in your database
        data = await request.json()
        better_auth_id = data.get("better_auth_id")
        user_email = data.get("email")

        # In a real implementation, you'd create a mapping between
        # Better Auth user IDs and your application's user profile data
        # For now, we'll simulate the linking process

        # You would typically store this mapping in a database table
        # that links Better Auth user IDs to your application user profiles
        link_data = {
            "better_auth_id": better_auth_id,
            "user_email": user_email,
            "status": "linked",
            "linked_at": "2023-01-01T00:00:00Z"
        }

        logger.info(f"Better Auth user linked: {better_auth_id}, email: {user_email}")
        return {"success": True, "data": link_data}
    except Exception as e:
        logger.error(f"Better Auth linking error: {e}")
        raise HTTPException(status_code=500, detail="Better Auth linking failed")