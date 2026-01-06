from django.shortcuts import get_object_or_404, redirect, render
from .models import Task
from django.contrib import messages as message
from django.contrib.auth.decorators import login_required
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
def tasks(request):
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