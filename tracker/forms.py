from django import forms
from django.contrib.auth.models import User
from .models import Project, ProgressUpdate, Notification

# 1. Main Project Form (Supervisor Only)
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description'] 
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500', 'rows': 3}),
        }

# 2. Progress Update Form (Regular Users)
class ProgressForm(forms.ModelForm):
    class Meta:
        model = ProgressUpdate
        fields = ['task_done', 'details', 'status']
        widgets = {
            'task_done': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'details': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500', 'rows': 4}),
            'status': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
        }

# 3. User Sign Up Form (Missing Piece Restored!)
class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
        }

# 4. Supervisor Alert & Broadcast Form
class NotificationForm(forms.ModelForm):
    recipient = forms.ModelChoiceField(
        queryset=User.objects.filter(is_superuser=False), 
        required=False, 
        empty_label="📢 Broadcast to Whole Group",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500'})
    )
    class Meta:
        model = Notification
        fields = ['recipient', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500', 'rows': 3, 'placeholder': 'Type announcement message...'}),
        }