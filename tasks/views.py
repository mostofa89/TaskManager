from django.shortcuts import get_object_or_404, redirect, render
from .models import Task
from django.contrib import messages as message
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import calendar
from datetime import datetime, timedelta
# Create your views here.

@login_required(login_url='user:user-login')
def createTask(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        priority = request.POST.get('priority')
        due_date = request.POST.get('due_date')
        status = request.POST.get('status')
        catagory = request.POST.get('category')
        is_completed = bool(request.POST.get('is_completed'))

        try:
            Task.objects.create(
                user=request.user,  # Set the logged-in user as task owner
                title=title,
                description=description,
                priority=priority,
                due_date=due_date,
                status=status,
                category=catagory,
                is_completed=is_completed
            )
            message.success(request, "Task created successfully.")
            return redirect('home')
        
        except Exception as e:
            message.error(request, f"Error creating task: {str(e)}")
            return render(request, 'tasks/create_task.html')
        

    return render(request, 'tasks/create_task.html')


@login_required(login_url='user:user-login')
def my_tasks(request):
    user_tasks = Task.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'tasks': user_tasks,
        'completed_count': user_tasks.filter(is_completed=True).count(),
        'in_progress_count': user_tasks.filter(status='in_progress').count(),
        'todo_count': user_tasks.filter(status='todo').count(),
    }
    return render(request, 'tasks/user_tasks.html', context)


@login_required(login_url='user:user-login')
def view_task(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    return render(request, 'tasks/view_task.html', {'task': task})


@login_required(login_url='user:user-login')
def edit_task(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == 'POST':
        task.title = request.POST.get('title')
        task.description = request.POST.get('description')
        task.priority = request.POST.get('priority')
        task.due_date = request.POST.get('due_date')
        task.status = request.POST.get('status')
        task.category = request.POST.get('category')
        task.is_completed = bool(request.POST.get('is_completed'))
        task.save()
        message.success(request, "Task updated successfully.")
        return redirect('tasks:user_tasks')

    return render(request, 'tasks/create_task.html', {'task': task, 'is_edit': True})


@login_required(login_url='user:user-login')
def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        task.delete()
        message.success(request, "Task deleted successfully.")
        return redirect('tasks:user_tasks')
    return redirect('tasks:user_tasks')


@login_required(login_url='user:user-login')
def complete_task(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        task.is_completed = not task.is_completed
        task.status = 'completed' if task.is_completed else 'todo'
        task.save()
        if task.is_completed:
            message.success(request, "Task marked as completed.")
        else:
            message.success(request, "Task marked as incomplete.")
    return redirect('tasks:user_tasks')


@login_required(login_url='user:user-login')
def calendar_view(request):
    # Get year and month from request or use current
    year = int(request.GET.get('year', datetime.now().year))
    month = int(request.GET.get('month', datetime.now().month))

    # Validate month/year
    if month > 12:
        month = 1
        year += 1
    elif month < 1:
        month = 12
        year -= 1

    # Get calendar for the month
    cal = calendar.monthcalendar(year, month)
    
    # Get all user tasks with due dates in this month
    start_date = datetime(year, month, 1).date()
    end_date = datetime(year, month, calendar.monthrange(year, month)[1]).date()
    
    user_tasks = Task.objects.filter(
        user=request.user,
        due_date__gte=start_date,
        due_date__lte=end_date
    ).order_by('due_date')
    
    # Create a dict of date -> list of tasks
    tasks_by_date = {}
    for task in user_tasks:
        date_key = task.due_date.day
        if date_key not in tasks_by_date:
            tasks_by_date[date_key] = []
        tasks_by_date[date_key].append(task)
    
    # Get month/year names
    month_name = calendar.month_name[month]
    
    # Navigation
    prev_month = month - 1
    prev_year = year
    if prev_month < 1:
        prev_month = 12
        prev_year -= 1
    
    next_month = month + 1
    next_year = year
    if next_month > 12:
        next_month = 1
        next_year += 1
    
    context = {
        'calendar': cal,
        'year': year,
        'month': month,
        'month_name': month_name,
        'tasks_by_date': tasks_by_date,
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
        'weekdays': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    }
    
    return render(request, 'tasks/calendar.html', context)