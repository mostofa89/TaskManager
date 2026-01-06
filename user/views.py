from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages as message
from django.contrib.auth import authenticate, logout as auth_logout, login as auth_login, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.core.mail import send_mail
from django.conf import settings
from .models import PasswordResetCode

# Create your views here.
def register(request):
    if request.method == 'POST':
        fname = request.POST.get('first_name')
        lname = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            message.error(request, "Passwords do not match.")
            return redirect('user:user-register')

        elif User.objects.filter(username=username).exists():
            message.error(request, "Username already taken.")
            return redirect('user:user-register')

        elif User.objects.filter(email=email).exists():
            message.error(request, "Email already registered.")
            return redirect('user:user-register')
        else:
            user = User.objects.create_user(
                username=username,
                password=password1,
                email=email,
                first_name=fname,
                last_name=lname
            )
            user.save()
            message.success(request, "Registration successful. You can now log in.")
            return redirect('user:user-login')


    return render(request, 'user/register.html')


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = authenticate(request, username=username, password=password)
            if user:
                auth_login(request, user)
                message.success(request, "Login successful.")
                return redirect('home')
            
            else:
                message.error(request, "Invalid username or password.")
                return redirect('user:user-login')
            
        except Exception as e:
            message.error(request, "An error occurred during login.")
            return redirect('user:user-login')
        
    return render(request, 'user/login.html')


def logout(request):
    auth_logout(request)
    message.success(request, "You have been logged out.")
    return redirect('home')


@login_required(login_url='user:user-login')
def profile(request):
    return render(request, 'user/profile.html')


@login_required(login_url='user:user-login')
def admin_profile(request):
    # Check if user is admin
    if not (request.user.is_staff or request.user.is_superuser):
        message.error(request, "You do not have permission to access this page.")
        return redirect('user:user-profile')
    
    # Get all users
    users = User.objects.all().order_by('-date_joined')
    
    # Calculate stats
    total_users = users.count()
    active_users = users.filter(is_active=True).count()
    admin_count = users.filter(is_staff=True).count()
    
    # Get total tasks count (will be 0 if tasks app not configured yet)
    try:
        from tasks.models import Task
        total_tasks = Task.objects.count()
    except:
        total_tasks = 0
    
    context = {
        'users': users,
        'total_users': total_users,
        'active_users': active_users,
        'admin_count': admin_count,
        'total_tasks': total_tasks,
    }
    return render(request, 'user/admin_profile.html', context)


@login_required(login_url='user:user-login')
def admin_create_user(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return HttpResponseForbidden("You do not have permission to perform this action.")
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        is_staff = request.POST.get('is_staff') == 'on'
        
        try:
            if User.objects.filter(username=username).exists():
                message.error(request, f"Username '{username}' already exists.")
            elif User.objects.filter(email=email).exists():
                message.error(request, f"Email '{email}' is already registered.")
            else:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                user.is_staff = is_staff
                user.save()
                message.success(request, f"User '{username}' created successfully.")
        except Exception as e:
            message.error(request, f"Error creating user: {str(e)}")
    
    return redirect('user:admin-profile')


@login_required(login_url='user:user-login')
def admin_edit_user(request, user_id):
    if not (request.user.is_staff or request.user.is_superuser):
        return HttpResponseForbidden("You do not have permission to perform this action.")
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        try:
            # Check if username is taken by another user
            if User.objects.filter(username=username).exclude(id=user_id).exists():
                message.error(request, f"Username '{username}' is already taken.")
            # Check if email is taken by another user
            elif User.objects.filter(email=email).exclude(id=user_id).exists():
                message.error(request, f"Email '{email}' is already registered.")
            else:
                user.username = username
                user.email = email
                user.first_name = first_name
                user.last_name = last_name
                user.save()
                message.success(request, f"User '{username}' updated successfully.")
        except Exception as e:
            message.error(request, f"Error updating user: {str(e)}")
    
    return redirect('user:admin-profile')


@login_required(login_url='user:user-login')
def admin_change_password(request, user_id):
    if not (request.user.is_staff or request.user.is_superuser):
        return HttpResponseForbidden("You do not have permission to perform this action.")
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password != confirm_password:
            message.error(request, "Passwords do not match.")
        elif len(new_password) < 6:
            message.error(request, "Password must be at least 6 characters long.")
        else:
            try:
                user.set_password(new_password)
                user.save()
                message.success(request, f"Password changed successfully for '{user.username}'.")
            except Exception as e:
                message.error(request, f"Error changing password: {str(e)}")
    
    return redirect('user:admin-profile')


@login_required(login_url='user:user-login')
def admin_delete_user(request, user_id):
    if not (request.user.is_staff or request.user.is_superuser):
        return HttpResponseForbidden("You do not have permission to perform this action.")
    
    user = get_object_or_404(User, id=user_id)
    
    # Prevent deleting yourself
    if user.id == request.user.id:
        message.error(request, "You cannot delete your own account.")
        return redirect('user:admin-profile')
    
    if request.method == 'POST':
        try:
            username = user.username
            user.delete()
            message.success(request, f"User '{username}' deleted successfully.")
        except Exception as e:
            message.error(request, f"Error deleting user: {str(e)}")
    
    return redirect('user:admin-profile')


@login_required(login_url='user:user-login')
def user_tasks(request, user_id):
    if not (request.user.is_staff or request.user.is_superuser):
        return HttpResponseForbidden("You do not have permission to view this page.")
    
    user = get_object_or_404(User, id=user_id)
    
    # Get tasks for this user (will handle if tasks app not configured)
    try:
        from tasks.models import Task
        tasks = Task.objects.filter(user=user).order_by('-created_at')
    except:
        tasks = []
    
    context = {
        'profile_user': user,
        'tasks': tasks,
    }
    return render(request, 'user/user_tasks.html', context)



def forgot_password(request):
    """Handle password reset with email verification"""
    step = request.POST.get('step', 'email') if request.method == 'POST' else 'email'
    
    if request.method == 'POST':
        # Step 1: User enters email
        if step == 'email':
            email = request.POST.get('email')
            try:
                user = User.objects.get(email=email)
                
                # Generate and save reset code
                reset_code = PasswordResetCode.objects.filter(user=user).first()
                if not reset_code:
                    reset_code = PasswordResetCode(user=user)
                
                reset_code.code = PasswordResetCode.generate_code()
                reset_code.is_used = False
                reset_code.save()
                
                # Send email with code
                subject = 'Password Reset Code - Task Manager'
                message_body = f"""
Hello {user.first_name or user.username},

You requested to reset your password. Your reset code is:

{reset_code.code}

This code will expire in 15 minutes.

If you didn't request this, please ignore this email.

Best regards,
Task Manager Team
                """
                
                send_mail(
                    subject,
                    message_body,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                
                message.success(request, f"Reset code sent to {email}")
                return render(request, 'user/forget_password.html', {
                    'step': 'verify',
                    'email': email
                })
                
            except User.DoesNotExist:
                # Don't reveal if email exists for security
                message.info(request, "If this email exists, you'll receive a reset code.")
                return render(request, 'user/forget_password.html', {'step': 'email'})
                
        # Step 2: User verifies code
        elif step == 'verify':
            email = request.POST.get('email')
            reset_code_input = request.POST.get('reset_code')
            
            try:
                user = User.objects.get(email=email)
                reset_code = PasswordResetCode.objects.get(user=user)
                
                # Check if code is valid
                if reset_code.is_expired():
                    message.error(request, "Reset code expired. Request a new one.")
                    return render(request, 'user/forget_password.html', {'step': 'email'})
                
                if reset_code.code != reset_code_input:
                    message.error(request, "Invalid reset code.")
                    return render(request, 'user/forget_password.html', {
                        'step': 'verify',
                        'email': email
                    })
                
                # Code is valid, proceed to password reset
                message.success(request, "Code verified! Now set your new password.")
                return render(request, 'user/forget_password.html', {
                    'step': 'reset',
                    'email': email
                })
                
            except (User.DoesNotExist, PasswordResetCode.DoesNotExist):
                message.error(request, "Invalid email or reset code.")
                return render(request, 'user/forget_password.html', {'step': 'email'})
        
        # Step 3: User sets new password
        elif step == 'reset':
            email = request.POST.get('email')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            # Validate passwords
            if not new_password or not confirm_password:
                message.error(request, "Both password fields are required.")
                return render(request, 'user/forget_password.html', {
                    'step': 'reset',
                    'email': email
                })
            
            if new_password != confirm_password:
                message.error(request, "Passwords do not match.")
                return render(request, 'user/forget_password.html', {
                    'step': 'reset',
                    'email': email
                })
            
            if len(new_password) < 6:
                message.error(request, "Password must be at least 6 characters long.")
                return render(request, 'user/forget_password.html', {
                    'step': 'reset',
                    'email': email
                })
            
            try:
                user = User.objects.get(email=email)
                reset_code = PasswordResetCode.objects.get(user=user)
                
                # Check if code is still valid
                if reset_code.is_expired():
                    message.error(request, "Reset code expired. Request a new one.")
                    return render(request, 'user/forget_password.html', {'step': 'email'})
                
                if reset_code.is_used:
                    message.error(request, "This code has already been used.")
                    return render(request, 'user/forget_password.html', {'step': 'email'})
                
                # Update password
                user.set_password(new_password)
                user.save()
                
                # Mark code as used
                reset_code.is_used = True
                reset_code.save()
                
                message.success(request, "Password reset successfully! You can now log in.")
                return redirect('user:user-login')
                
            except (User.DoesNotExist, PasswordResetCode.DoesNotExist):
                message.error(request, "Invalid email or session expired.")
                return render(request, 'user/forget_password.html', {'step': 'email'})
    
    return render(request, 'user/forget_password.html', {'step': 'email'})


def dashboard(request):
    return render(request, 'user/dashboard.html')


@login_required(login_url='user:user-login')
def change_password(request):
    """Change password using Django's built-in PasswordChangeForm for validation."""
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # keep user logged in after password change
            message.success(request, "Password changed successfully.")
            return redirect('user:user-profile')
        else:
            # Form errors will be rendered in the template
            message.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'user/change_password.html', {'form': form})