"""
Pydantic schemas defining the contract for user identity and authentication
across the Presentation (API) and Service Layers.
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

# --- Input Schemas (Requests / Commands) ---


class UserRequest(BaseModel):
    """
    Schema for user creation requests. Used by the Service Layer for registration
    and initial account entity creation.
    """

    email: EmailStr = Field(..., description="User's unique email address")
    name: str = Field(..., min_length=1, max_length=255, description="User's full name or display name")

    # Password must be provided for initial creation, but Optional here for cleaner structure
    # if this schema were ever reused for updates without a password change.
    password: str | None = Field(
        default=None, min_length=8, description="User's password (min 8 characters, will be hashed)"
    )

    is_active: bool = Field(default=True, description="Whether the user account is active")
    avatar: str | None = Field(default=None, description="URL to user's avatar image")


class ProfileRequest(BaseModel):
    """
    Schema for updating user profile fields. Fields are optional as they are updates.
    """

    email: EmailStr | None = Field(default=None, description="User's email address")
    name: str | None = Field(default=None, min_length=1, max_length=255, description="User's full name")
    is_active: bool | None = Field(default=None, description="Whether the user account is active")
    avatar: str | None = Field(default=None, description="URL to user's avatar image")


class PasswordChangeRequest(BaseModel):
    """
    Schema for changing password (requires old password verification).
    Used by the UserService to verify the current credential before update.
    """

    old_password: str = Field(..., description="Current password for verification")
    new_password: str = Field(..., min_length=8, description="New password (minimum 8 characters)")


class LoginRequest(BaseModel):
    """
    Minimal schema for user authentication/login command.
    """

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's plain text password")


# --- Output Schema (Response / Domain Object) ---


class UserResponse(BaseModel):
    """
    Response schema for user information. Also serves as the core Domain Model
    returned by the UserService.
    """

    # Configuration allows mapping from SQLAlchemy ORM objects
    model_config = {"from_attributes": True}

    id: int = Field(..., description="User ID")
    email: str = Field(..., description="User's email address")
    name: str = Field(..., description="User's full name")
    avatar: str | None = Field(default=None, description="URL to user's avatar image")
    is_active: bool | None = Field(default=None, description="Whether the user account is active")

    # Include audit fields for completeness in the response
    created_at: datetime = Field(..., description="Date and time of user creation")
    updated_at: datetime = Field(..., description="Date and time of last update")
