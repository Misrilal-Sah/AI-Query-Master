"""
AI Query Master - Authentication API
Uses Supabase Auth for signup, login, Google OAuth, forgot password.
"""
import os
import logging
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from typing import Optional

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# Lazy Supabase client
def _get_supabase():
    from db.supabase_client import get_supabase_client
    client = get_supabase_client()
    if not client.is_available:
        raise HTTPException(503, "Supabase not configured")
    return client.client


class SignupRequest(BaseModel):
    email: str = Field(..., description="User email")
    password: str = Field(..., min_length=6, description="Password (min 6 chars)")
    full_name: Optional[str] = Field(default="", description="Full name")


class LoginRequest(BaseModel):
    email: str
    password: str


class ForgotPasswordRequest(BaseModel):
    email: str


@router.post("/signup")
async def signup(request: SignupRequest):
    """Register a new user with email and password."""
    try:
        supabase = _get_supabase()
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        result = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password,
            "options": {
                "data": {
                    "full_name": request.full_name or request.email.split("@")[0],
                },
                "email_redirect_to": f"{frontend_url}/auth/callback",
            },
        })

        if result.user:
            # Supabase returns a user with empty identities if email already exists
            # (to prevent email enumeration) — detect and show friendly error
            if hasattr(result.user, 'identities') and result.user.identities is not None and len(result.user.identities) == 0:
                raise HTTPException(400, "An account with this email already exists. Please sign in instead.")

            return {
                "success": True,
                "message": "Account created! Please check your email to confirm.",
                "user": {
                    "id": result.user.id,
                    "email": result.user.email,
                    "full_name": request.full_name,
                },
            }
        else:
            raise HTTPException(400, "Signup failed")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(400, str(e))


@router.post("/login")
async def login(request: LoginRequest):
    """Login with email and password."""
    try:
        supabase = _get_supabase()
        result = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password,
        })

        if result.user and result.session:
            user_meta = result.user.user_metadata or {}
            return {
                "success": True,
                "user": {
                    "id": result.user.id,
                    "email": result.user.email,
                    "full_name": user_meta.get("full_name", result.user.email.split("@")[0]),
                },
                "access_token": result.session.access_token,
            }
        else:
            raise HTTPException(401, "Invalid credentials")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(401, "Invalid email or password")


@router.get("/google")
async def google_auth():
    """Redirect to Google OAuth via Supabase."""
    try:
        supabase = _get_supabase()
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")

        result = supabase.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirect_to": f"{frontend_url}/auth/callback",
            },
        })

        if result and result.url:
            return RedirectResponse(url=result.url)
        else:
            raise HTTPException(500, "Failed to initiate Google auth")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google auth error: {e}")
        raise HTTPException(500, str(e))


@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    """Send password reset email."""
    try:
        supabase = _get_supabase()
        supabase.auth.reset_password_email(
            request.email,
            options={
                "redirect_to": os.getenv("FRONTEND_URL", "http://localhost:5173") + "/reset-password",
            },
        )

        return {
            "success": True,
            "message": "If an account exists, a reset link has been sent.",
        }

    except Exception as e:
        logger.error(f"Forgot password error: {e}")
        # Don't reveal if email exists
        return {
            "success": True,
            "message": "If an account exists, a reset link has been sent.",
        }


class ExchangeCodeRequest(BaseModel):
    code: str = Field(..., description="Auth code from OAuth callback")


class UpdatePasswordRequest(BaseModel):
    access_token: str
    new_password: str


@router.post("/update-password")
async def update_password(request: UpdatePasswordRequest):
    """Update password using recovery access token."""
    try:
        from supabase import create_client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        # Create a new client with the user's access token
        client = create_client(supabase_url, supabase_key)
        client.auth.set_session(request.access_token, "")
        result = client.auth.update_user({"password": request.new_password})

        if result.user:
            return {"success": True, "message": "Password updated successfully"}
        else:
            raise HTTPException(400, "Failed to update password")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update password error: {e}")
        raise HTTPException(400, f"Password update failed: {str(e)}")


@router.post("/exchange-code")
async def exchange_code(request: ExchangeCodeRequest):
    """Exchange a PKCE auth code for a session (Google OAuth callback)."""
    try:
        supabase = _get_supabase()
        result = supabase.auth.exchange_code_for_session({"auth_code": request.code})

        if result.user and result.session:
            user_meta = result.user.user_metadata or {}
            return {
                "success": True,
                "user": {
                    "id": result.user.id,
                    "email": result.user.email,
                    "full_name": user_meta.get("full_name", user_meta.get("name", result.user.email.split("@")[0])),
                },
                "access_token": result.session.access_token,
            }
        else:
            raise HTTPException(400, "Failed to exchange code")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Code exchange error: {e}")
        raise HTTPException(400, f"Code exchange failed: {str(e)}")
