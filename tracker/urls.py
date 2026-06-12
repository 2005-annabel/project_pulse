from django.urls import path
from . import views

urlpatterns = [
    path('', views.project_list, name='project_list'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path('project/new-main/', views.create_main_project, name='create_main_project'),
    path('project/<int:project_pk>/log-progress/', views.log_progress, name='log_progress'),
    path('progress/<int:pk>/edit/', views.edit_progress, name='edit_progress'),
    path('progress/<int:pk>/delete/', views.delete_progress, name='delete_progress'),
    
    path('supervisor/announcement/', views.send_announcement, name='send_announcement'),
    path('supervisor/toggle-lock/<int:pk>/', views.toggle_permission, name='toggle_permission'),
    path('notification/<int:pk>/dismiss/', views.dismiss_notification, name='dismiss_notification'),
]