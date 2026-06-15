from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Dashboard Matrix
    path('', views.project_list, name='project_list'),
    
    # Core Authentication System Paths
    path('login/', auth_views.LoginView.as_view(template_name='tracker/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup_view, name='signup'),
    
    # Inline Progress Entry Controls
    path('progress/<int:pk>/edit/', views.edit_progress, name='edit_progress'),
    path('progress/<int:pk>/delete/', views.delete_progress, name='delete_progress'),
    path('notification/<int:pk>/dismiss/', views.dismiss_notification, name='dismiss_notification'),
    
    # Supervisor Management Overrides
    path('progress/<int:pk>/toggle-update/', views.toggle_update_permission, name='toggle_update_permission'),
    path('progress/<int:pk>/toggle-delete/', views.toggle_delete_permission, name='toggle_delete_permission'),
    
    # Operational Generation Tasks
    path('project/create/', views.create_main_project, name='create_main_project'),  
    path('announcement/send/', views.send_announcement, name='send_announcement'), 
]