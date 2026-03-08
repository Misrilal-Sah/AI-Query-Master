# Supabase Email Templates — Dark Theme

## How to Apply
Go to **Supabase Dashboard → Authentication → Email Templates**

For each template below, paste the HTML into the corresponding template editor.

---

## 1. Confirm Signup

**Subject:** Confirm your AI Query Master account

```html
<html>
<body style="margin:0;padding:0;background-color:#0a0e1a;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#0a0e1a;padding:40px 0;">
    <tr><td align="center">
      <table width="500" cellpadding="0" cellspacing="0" style="background:#111827;border:1px solid rgba(59,130,246,0.2);border-radius:16px;overflow:hidden;">
        <!-- Header -->
        <tr><td style="background:linear-gradient(135deg,#3b82f6,#8b5cf6);padding:32px;text-align:center;">
          <table cellpadding="0" cellspacing="0" style="margin:0 auto 12px;">
            <tr><td style="width:50px;height:50px;background:rgba(255,255,255,0.2);border-radius:10px;text-align:center;vertical-align:middle;font-weight:800;font-size:18px;color:white;line-height:50px;">QM</td></tr>
          </table>
          <h1 style="color:white;font-size:22px;margin:8px 0 0;">AI Query Master</h1>
        </td></tr>
        <!-- Body -->
        <tr><td style="padding:36px 32px;">
          <h2 style="color:#f1f5f9;font-size:20px;margin:0 0 12px;">Welcome! Confirm Your Email</h2>
          <p style="color:#94a3b8;font-size:15px;line-height:1.6;margin:0 0 24px;">
            Thanks for signing up for AI Query Master. Click the button below to verify your email address and start analyzing database queries with AI.
          </p>
          <div style="text-align:center;margin:28px 0;">
            <a href="{{ .ConfirmationURL }}" style="background:linear-gradient(135deg,#3b82f6,#8b5cf6);color:white;padding:14px 36px;border-radius:8px;font-weight:600;font-size:15px;text-decoration:none;display:inline-block;">
              ✓ Confirm My Email
            </a>
          </div>
          <p style="color:#64748b;font-size:13px;line-height:1.5;margin:24px 0 0;">
            If you didn't create an account, you can safely ignore this email.
          </p>
        </td></tr>
        <!-- Footer -->
        <tr><td style="padding:20px 32px;border-top:1px solid rgba(59,130,246,0.15);text-align:center;">
          <p style="color:#475569;font-size:12px;margin:0;">
            AI Query Master — AI-Powered Database Assistant
          </p>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body>
</html>
```

---

## 2. Reset Password

**Subject:** Reset your AI Query Master password

```html
<html>
<body style="margin:0;padding:0;background-color:#0a0e1a;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#0a0e1a;padding:40px 0;">
    <tr><td align="center">
      <table width="500" cellpadding="0" cellspacing="0" style="background:#111827;border:1px solid rgba(59,130,246,0.2);border-radius:16px;overflow:hidden;">
        <!-- Header -->
        <tr><td style="background:linear-gradient(135deg,#f59e0b,#ef4444);padding:32px;text-align:center;">
          <table cellpadding="0" cellspacing="0" style="margin:0 auto 12px;">
            <tr><td style="width:50px;height:50px;background:rgba(255,255,255,0.2);border-radius:10px;text-align:center;vertical-align:middle;font-weight:800;font-size:18px;color:white;line-height:50px;">QM</td></tr>
          </table>
          <h1 style="color:white;font-size:22px;margin:8px 0 0;">AI Query Master</h1>
        </td></tr>
        <!-- Body -->
        <tr><td style="padding:36px 32px;">
          <h2 style="color:#f1f5f9;font-size:20px;margin:0 0 12px;">Reset Your Password</h2>
          <p style="color:#94a3b8;font-size:15px;line-height:1.6;margin:0 0 24px;">
            We received a request to reset your password. Click the button below to choose a new password. This link will expire in 1 hour.
          </p>
          <div style="text-align:center;margin:28px 0;">
            <a href="{{ .ConfirmationURL }}" style="background:linear-gradient(135deg,#f59e0b,#ef4444);color:white;padding:14px 36px;border-radius:8px;font-weight:600;font-size:15px;text-decoration:none;display:inline-block;">
              🔑 Reset Password
            </a>
          </div>
          <p style="color:#64748b;font-size:13px;line-height:1.5;margin:24px 0 0;">
            If you didn't request a password reset, you can safely ignore this email. Your password will remain unchanged.
          </p>
        </td></tr>
        <!-- Footer -->
        <tr><td style="padding:20px 32px;border-top:1px solid rgba(59,130,246,0.15);text-align:center;">
          <p style="color:#475569;font-size:12px;margin:0;">
            AI Query Master — AI-Powered Database Assistant
          </p>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body>
</html>
```

---

## 3. Magic Link (optional)

**Subject:** Your AI Query Master login link

```html
<html>
<body style="margin:0;padding:0;background-color:#0a0e1a;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#0a0e1a;padding:40px 0;">
    <tr><td align="center">
      <table width="500" cellpadding="0" cellspacing="0" style="background:#111827;border:1px solid rgba(59,130,246,0.2);border-radius:16px;overflow:hidden;">
        <tr><td style="background:linear-gradient(135deg,#10b981,#06b6d4);padding:32px;text-align:center;">
          <table cellpadding="0" cellspacing="0" style="margin:0 auto 12px;">
            <tr><td style="width:50px;height:50px;background:rgba(255,255,255,0.2);border-radius:10px;text-align:center;vertical-align:middle;font-weight:800;font-size:18px;color:white;line-height:50px;">QM</td></tr>
          </table>
          <h1 style="color:white;font-size:22px;margin:8px 0 0;">AI Query Master</h1>
        </td></tr>
        <tr><td style="padding:36px 32px;">
          <h2 style="color:#f1f5f9;font-size:20px;margin:0 0 12px;">Your Login Link</h2>
          <p style="color:#94a3b8;font-size:15px;line-height:1.6;margin:0 0 24px;">
            Click the button below to sign in to AI Query Master. This link expires in 10 minutes.
          </p>
          <div style="text-align:center;margin:28px 0;">
            <a href="{{ .ConfirmationURL }}" style="background:linear-gradient(135deg,#10b981,#06b6d4);color:white;padding:14px 36px;border-radius:8px;font-weight:600;font-size:15px;text-decoration:none;display:inline-block;">
              🔗 Sign In
            </a>
          </div>
        </td></tr>
        <tr><td style="padding:20px 32px;border-top:1px solid rgba(59,130,246,0.15);text-align:center;">
          <p style="color:#475569;font-size:12px;margin:0;">AI Query Master — AI-Powered Database Assistant</p>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body>
</html>
```
