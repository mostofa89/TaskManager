# Password Reset Feature Guide

## Overview
The password reset feature allows users to securely reset their password if forgotten. The system uses **6-digit numeric codes** sent via email, which expire after **15 minutes**.

## Features
- ✅ Email-based password reset
- ✅ 6-digit verification codes
- ✅ 15-minute code expiration
- ✅ One-time use codes (prevent replay attacks)
- ✅ Secure password hashing via Django
- ✅ Security: Doesn't reveal if email exists
- ✅ Integration with existing Django auth system

## How It Works

### Step 1: Request Reset Code
1. User clicks "Forgot Password?" on login page
2. User enters their email address
3. System generates a random 6-digit code
4. Code is stored in database with 15-minute expiration
5. Email is sent to user with the code

### Step 2: Verify Code
1. User receives email with 6-digit code
2. User enters code on the verification page
3. System validates code:
   - Code exists in database
   - Code belongs to entered email
   - Code hasn't expired (15 minutes)
   - Code hasn't been used yet
4. If valid, proceed to password reset step

### Step 3: Reset Password
1. User enters new password
2. User confirms password match
3. System validates:
   - Passwords match
   - Password is at least 6 characters
4. Password is hashed and saved via Django's `set_password()`
5. Code is marked as "used" to prevent reuse
6. User is redirected to login

## Database Model

### PasswordResetCode
- `user`: OneToOne relation to User (the user requesting reset)
- `code`: String, 6-digit numeric code
- `is_used`: Boolean, true after password reset
- `created_at`: DateTime, timestamp of code generation
- `is_expired()`: Method to check if 15 minutes have passed

## Views

### forgot_password (GET)
- Displays password reset form
- Step 1 (email): Email input field
- Step 2 (verify): 6-digit code input
- Step 3 (reset): New password + confirm password

### forgot_password (POST)
Handles three different steps:

1. **Email Submission** (`step='email'`)
   - Validates email exists in User model
   - Generates and stores PasswordResetCode
   - Sends email with code
   - Redirects to code verification step
   - Returns generic message (doesn't reveal if email exists)

2. **Code Verification** (`step='verify'`)
   - Validates 6-digit code
   - Checks code exists and hasn't expired
   - Checks code hasn't been used
   - Renders password reset form

3. **Password Reset** (`step='reset'`)
   - Validates password length (6+ chars)
   - Validates password confirmation
   - Hashes and saves new password
   - Marks code as used
   - Redirects to login with success message

## Configuration

### Local Development (Console Output)

In `.env` or settings:
```
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

Verification codes appear in Django development server console.

### Production with Gmail

In `.env` on Render or your server:
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

⚠️ **Important**: For Gmail, use an **app-specific password**, not your regular password.

Steps to get Gmail app password:
1. Enable 2-Factor Authentication on your Google account
2. Go to https://myaccount.google.com/apppasswords
3. Select "Mail" and "Windows Computer"
4. Google will generate a 16-character password
5. Use this as EMAIL_HOST_PASSWORD

### Production with SendGrid

In `.env`:
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

### Production with Mailgun

In `.env`:
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_HOST_USER=postmaster@yourdomain.com
EMAIL_HOST_PASSWORD=your-mailgun-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

## Testing Locally

1. **Ensure EMAIL_BACKEND is set to console backend**
   ```
   EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
   ```

2. **Run development server**
   ```bash
   python manage.py runserver
   ```

3. **Navigate to password reset**
   - Go to: http://localhost:8000/user/login/
   - Click "Forgot Password?"
   - Enter your email

4. **Copy code from console**
   - Check Django development server console
   - Copy the 6-digit code from the email output

5. **Enter code and reset password**
   - Return to browser
   - Paste the 6-digit code
   - Enter new password
   - Confirm and submit

6. **Login with new password**
   - Try logging in with new password

## Testing on Render

Before deploying, ensure:

1. **Email credentials are set in Render environment**
   - Go to Render dashboard → Your Service → Environment
   - Add all EMAIL_* variables
   - Redeploy

2. **Database is configured**
   - PasswordResetCode model requires migration
   - Migrations run automatically in `build.sh`

3. **Test password reset on live site**
   - Check your actual email inbox for code
   - Verify code works

## Troubleshooting

### "This email is not registered"
- User email doesn't exist in database
- User needs to create account first

### "Invalid code" or "Code expired"
- Code doesn't exist, expired, or already used
- User can request new code
- Code expires after 15 minutes

### "Passwords do not match"
- Entered passwords don't match
- User needs to re-enter carefully

### Email not received
- Check email backend configuration
- For console: Check Django development server console
- For SMTP: Check EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
- Check spam/junk folder
- Ensure credentials are correct

### "DisallowedHost" error on Render
- ALLOWED_HOSTS not configured correctly
- Should be auto-detected if DEBUG=False
- Check Render environment variables

## Security Considerations

✅ **Implemented**
- 6-digit codes are random and unpredictable
- Codes expire after 15 minutes
- Codes are one-time use (marked as used after reset)
- Password is hashed via Django's `set_password()`
- Doesn't reveal if email exists (security by obscurity)
- No URL tokens (tokens can be leaked in logs/history)

⚠️ **Additional Measures**
- Consider adding rate limiting to prevent code brute-force
- Consider adding "maximum attempts" before locking email
- Consider sending "password changed" notification email
- Consider logging password reset events for security audit

## Files Modified

1. **user/models.py**
   - Added `PasswordResetCode` model

2. **user/views.py**
   - Added `forgot_password()` view with 3-step flow
   - Email generation and verification logic

3. **user/urls.py**
   - Added route: `path('forgot-password/', forgot_password, name='forgot-password')`

4. **templates/user/forget_password.html**
   - Multi-step form template
   - Step 1: Email input
   - Step 2: Code verification
   - Step 3: Password reset

5. **templates/user/login.html**
   - Updated "Forgot Password?" link to new route

6. **Task_Manager/settings.py**
   - Email backend configuration
   - Support for environment variables

7. **user/migrations/0001_initial.py**
   - Auto-generated migration for PasswordResetCode model

## Next Steps

1. **Local Testing**
   - Test with console email backend
   - Verify all 3 steps work

2. **Configure Email for Render**
   - Choose email provider (Gmail, SendGrid, Mailgun, etc.)
   - Get SMTP credentials
   - Set environment variables on Render

3. **Deploy**
   - Push code: `git push origin main`
   - Redeploy on Render: Manual Deploy → Clear build cache

4. **Test on Production**
   - Test password reset on live site
   - Verify emails are received

5. **Monitor**
   - Monitor Django logs for email errors
   - Check email delivery rates
   - Monitor for suspicious password reset attempts

## API Reference

### PasswordResetCode.generate_code()
Static method that generates a random 6-digit numeric code.

```python
code = PasswordResetCode.generate_code()  # Returns string like "123456"
```

### PasswordResetCode.is_expired()
Instance method that checks if code has expired (> 15 minutes old).

```python
prc = PasswordResetCode.objects.get(user=user)
if prc.is_expired():
    # Code is expired, user must request new one
```

### send_mail()
Django built-in function used to send emails.

```python
send_mail(
    subject='Password Reset Code',
    message=f'Your reset code is: {code}',
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=[email],
    fail_silently=False,
)
```

## Support

For issues with:
- **Django auth**: See [Django Authentication System](https://docs.djangoproject.com/en/6.0/topics/auth/)
- **Email configuration**: See [Django Email Backend](https://docs.djangoproject.com/en/6.0/topics/email/)
- **Render deployment**: See [Render Python Deployment](https://render.com/docs/deploy-python)
- **Gmail app passwords**: See [Google App Passwords](https://support.google.com/accounts/answer/185833)
