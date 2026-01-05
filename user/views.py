from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages as message
from django.contrib.auth import authenticate, logout as auth_logout, login as auth_login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

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