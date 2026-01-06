from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('create/', views.createTask, name='create'),
    path('my-tasks/', views.my_tasks, name='user_tasks'),
    path('<int:pk>/', views.view_task, name='view'),
    path('<int:pk>/edit/', views.edit_task, name='edit'),
    path('<int:pk>/delete/', views.delete_task, name='delete'),
    path('<int:pk>/complete/', views.complete_task, name='complete'),
]