from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Built-in Django Admin portal
    path('admin/', admin.site.urls),
    
    # This automatically includes ALL routes from your tracker/urls.py (including login, signup, and project_list)
    path('', include('tracker.urls')), 
]