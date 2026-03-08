"""
AI Query Master - Email Template Preview Endpoint
GET /api/email-templates/confirmation  → Preview confirmation email
GET /api/email-templates/reset-password → Preview reset password email
"""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/api/email-templates", tags=["Email Templates"])

CONFIRMATION_TEMPLATE = """<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background-color:#050816;font-family:'Segoe UI',Roboto,Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#050816;padding:48px 0;">
    <tr><td align="center">
      <table width="520" cellpadding="0" cellspacing="0" style="background:linear-gradient(145deg,#0f172a 0%,#1a1f3a 100%);border:1px solid rgba(59,130,246,0.2);border-radius:20px;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,0.5),0 0 40px rgba(59,130,246,0.08);">
        <!-- Header with gradient -->
        <tr><td style="padding:0;">
          <div style="background:linear-gradient(135deg,#3b82f6 0%,#8b5cf6 50%,#06b6d4 100%);padding:40px 32px;text-align:center;">
            <table cellpadding="0" cellspacing="0" style="margin:0 auto;">
              <tr><td style="background:rgba(255,255,255,0.15);border-radius:12px;width:56px;height:56px;text-align:center;vertical-align:middle;">
                <span style="font-weight:800;font-size:20px;color:white;line-height:56px;">QM</span>
              </td></tr>
            </table>
            <h1 style="color:white;font-size:24px;font-weight:800;margin:16px 0 4px;letter-spacing:-0.5px;">AI Query Master</h1>
            <p style="color:rgba(255,255,255,0.7);font-size:13px;margin:0;">AI-Powered Database Assistant</p>
          </div>
        </td></tr>
        <!-- Body -->
        <tr><td style="padding:40px 36px;">
          <h2 style="color:#f1f5f9;font-size:22px;font-weight:700;margin:0 0 8px;">Verify Your Email ✨</h2>
          <p style="color:#94a3b8;font-size:15px;line-height:1.7;margin:0 0 28px;">
            Welcome to AI Query Master! You're one step away from analyzing, optimizing, and generating database queries with AI intelligence.
          </p>
          
          <!-- CTA Button -->
          <table width="100%" cellpadding="0" cellspacing="0">
            <tr><td align="center" style="padding:4px 0 28px;">
              <a href="{{ .ConfirmationURL }}" style="background:linear-gradient(135deg,#3b82f6,#8b5cf6);color:white;padding:16px 48px;border-radius:12px;font-weight:700;font-size:16px;text-decoration:none;display:inline-block;box-shadow:0 4px 20px rgba(59,130,246,0.4);">
                Confirm My Email
              </a>
            </td></tr>
          </table>

          <!-- What you get -->
          <div style="background:rgba(59,130,246,0.06);border:1px solid rgba(59,130,246,0.12);border-radius:12px;padding:20px 24px;margin-bottom:24px;">
            <p style="color:#e2e8f0;font-size:13px;font-weight:600;margin:0 0 12px;">What you can do:</p>
            <table cellpadding="0" cellspacing="0" width="100%">
              <tr><td style="padding:4px 0;color:#94a3b8;font-size:13px;">⚡ Review & optimize SQL queries</td></tr>
              <tr><td style="padding:4px 0;color:#94a3b8;font-size:13px;">🗄️ Analyze database schemas</td></tr>
              <tr><td style="padding:4px 0;color:#94a3b8;font-size:13px;">💬 Convert natural language to SQL</td></tr>
              <tr><td style="padding:4px 0;color:#94a3b8;font-size:13px;">🔗 Connect to live databases</td></tr>
            </table>
          </div>

          <p style="color:#475569;font-size:12px;line-height:1.5;margin:0;">
            If you didn't create this account, you can safely ignore this email. This link expires in 24 hours.
          </p>
        </td></tr>
        <!-- Footer -->
        <tr><td style="padding:20px 36px 24px;border-top:1px solid rgba(59,130,246,0.1);text-align:center;">
          <p style="color:#475569;font-size:11px;margin:0;">
            © 2026 AI Query Master · Built with AI Intelligence
          </p>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""

RESET_PASSWORD_TEMPLATE = """<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background-color:#050816;font-family:'Segoe UI',Roboto,Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#050816;padding:48px 0;">
    <tr><td align="center">
      <table width="520" cellpadding="0" cellspacing="0" style="background:linear-gradient(145deg,#0f172a 0%,#1a1f3a 100%);border:1px solid rgba(245,158,11,0.2);border-radius:20px;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,0.5),0 0 40px rgba(245,158,11,0.08);">
        <!-- Header with gradient -->
        <tr><td style="padding:0;">
          <div style="background:linear-gradient(135deg,#f59e0b 0%,#ef4444 50%,#ec4899 100%);padding:40px 32px;text-align:center;">
            <table cellpadding="0" cellspacing="0" style="margin:0 auto;">
              <tr><td style="background:rgba(255,255,255,0.15);border-radius:12px;width:56px;height:56px;text-align:center;vertical-align:middle;">
                <span style="font-weight:800;font-size:20px;color:white;line-height:56px;">QM</span>
              </td></tr>
            </table>
            <h1 style="color:white;font-size:24px;font-weight:800;margin:16px 0 4px;letter-spacing:-0.5px;">AI Query Master</h1>
            <p style="color:rgba(255,255,255,0.7);font-size:13px;margin:0;">Password Reset Request</p>
          </div>
        </td></tr>
        <!-- Body -->
        <tr><td style="padding:40px 36px;">
          <h2 style="color:#f1f5f9;font-size:22px;font-weight:700;margin:0 0 8px;">Reset Your Password 🔑</h2>
          <p style="color:#94a3b8;font-size:15px;line-height:1.7;margin:0 0 28px;">
            We received a request to reset your password. Click the button below to choose a new password for your AI Query Master account.
          </p>
          
          <!-- CTA Button -->
          <table width="100%" cellpadding="0" cellspacing="0">
            <tr><td align="center" style="padding:4px 0 28px;">
              <a href="{{ .ConfirmationURL }}" style="background:linear-gradient(135deg,#f59e0b,#ef4444);color:white;padding:16px 48px;border-radius:12px;font-weight:700;font-size:16px;text-decoration:none;display:inline-block;box-shadow:0 4px 20px rgba(245,158,11,0.4);">
                Reset Password
              </a>
            </td></tr>
          </table>

          <!-- Security notice -->
          <div style="background:rgba(245,158,11,0.06);border:1px solid rgba(245,158,11,0.12);border-radius:12px;padding:16px 20px;margin-bottom:24px;">
            <p style="color:#f59e0b;font-size:13px;font-weight:600;margin:0 0 4px;">⚠️ Security Notice</p>
            <p style="color:#94a3b8;font-size:12px;line-height:1.5;margin:0;">
              This link expires in 1 hour. If you didn't request this, your account is secure — someone may have entered your email by mistake.
            </p>
          </div>

          <p style="color:#475569;font-size:12px;line-height:1.5;margin:0;">
            If you didn't request a password reset, no action is needed. Your password will remain unchanged.
          </p>
        </td></tr>
        <!-- Footer -->
        <tr><td style="padding:20px 36px 24px;border-top:1px solid rgba(245,158,11,0.1);text-align:center;">
          <p style="color:#475569;font-size:11px;margin:0;">
            © 2026 AI Query Master · Built with AI Intelligence
          </p>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


@router.get("/confirmation", response_class=HTMLResponse)
async def preview_confirmation():
    """Preview the confirmation email template."""
    # Replace template variable with # for preview
    html = CONFIRMATION_TEMPLATE.replace("{{ .ConfirmationURL }}", "#")
    return HTMLResponse(content=html)


@router.get("/reset-password", response_class=HTMLResponse)
async def preview_reset_password():
    """Preview the reset password email template."""
    html = RESET_PASSWORD_TEMPLATE.replace("{{ .ConfirmationURL }}", "#")
    return HTMLResponse(content=html)


def get_confirmation_html():
    """Return raw confirmation template HTML for Supabase config."""
    return CONFIRMATION_TEMPLATE


def get_reset_password_html():
    """Return raw reset password template HTML for Supabase config."""
    return RESET_PASSWORD_TEMPLATE
