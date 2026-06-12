from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Fixed: Changed admin.site.get_urls() to admin.site.urls
    path('admin/', admin.site.urls),
    
    # Fixed: Changed 'tracker/urls.py' to Python module dot-notation 'tracker.urls'
    path('', include('tracker.urls')), 
]