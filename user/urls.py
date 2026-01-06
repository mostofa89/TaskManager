from django.contrib import admin
from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    path('register/', views.register, name='user-register'),
    path('login/', views.login, name='user-login'),
    path('logout/', views.logout, name='user-logout'),
    path('profile/', views.profile, name='user-profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('dashboard/', views.dashboard, name='user-dashboard'),
    path('change-password/', views.change_password, name='change-password'),
    path('forgot-password/', views.forgot_password, name='forgot-password'),
    
    # Admin routes
    path('admin/dashboard/', views.admin_profile, name='admin-profile'),
    path('admin/create/', views.admin_create_user, name='admin-create-user'),
    path('admin/edit/<int:user_id>/', views.admin_edit_user, name='admin-edit-user'),
    path('admin/password/<int:user_id>/', views.admin_change_password, name='admin-change-password'),
    path('admin/delete/<int:user_id>/', views.admin_delete_user, name='admin-delete-user'),
    path('admin/tasks/<int:user_id>/', views.user_tasks, name='user-tasks'),
]