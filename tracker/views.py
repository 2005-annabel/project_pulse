from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Project, ProgressUpdate, Notification

@login_required
def project_list(request):
    if request.method == 'POST':
        task_done = request.POST.get('task_done')
        details = request.POST.get('details')
        if task_done and details:
            ProgressUpdate.objects.create(
                user=request.user,
                task_done=task_done,
                details=details
            )
            return redirect('project_list')

    projects = Project.objects.all()
    updates = ProgressUpdate.objects.all().order_by('-created_at')
    
    # --- UPDATED: Get only alerts meant for this user OR group broadcasts ---
    alerts = Notification.objects.filter(
        Q(recipient=request.user) | Q(recipient__isnull=True)
    ).order_by('-created_at')
    
    return render(request, 'tracker/project_list.html', {
        'projects': projects,
        'updates': updates,
        'alerts': alerts
    })

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('project_list')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('project_list')
    else:
        form = UserCreationForm()
    return render(request, 'tracker/signup.html', {'form': form})

@login_required
def edit_progress(request, pk):
    update = get_object_or_404(ProgressUpdate, pk=pk)
    if update.user != request.user and not request.user.is_superuser:
        return redirect('project_list')
    if request.method == 'POST':
        update.task_done = request.POST.get('task_done')
        update.details = request.POST.get('details')
        update.save()
        return redirect('project_list')
    return render(request, 'tracker/edit_progress.html', {'update': update})

@login_required
def delete_progress(request, pk):
    update = get_object_or_404(ProgressUpdate, pk=pk)
    if update.user == request.user or request.user.is_superuser:
        update.delete()
    return redirect('project_list')

@login_required
def dismiss_notification(request, pk):
    alert = get_object_or_404(Notification, pk=pk)
    # Security: Ensure only the recipient or an admin can clear it
    if alert.recipient == request.user or request.user.is_superuser or alert.recipient is None:
        alert.delete()
    return redirect('project_list')

@login_required
def toggle_update_permission(request, pk):
    if request.user.is_superuser:
        update = get_object_or_404(ProgressUpdate, pk=pk)
        update.can_update = not update.can_update
        update.save()
    return redirect('project_list')

@login_required
def toggle_delete_permission(request, pk):
    if request.user.is_superuser:
        update = get_object_or_404(ProgressUpdate, pk=pk)
        update.can_delete = not update.can_delete
        update.save()
    return redirect('project_list')

@login_required
def create_main_project(request):
    if not request.user.is_superuser:
        return redirect('project_list')
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        if title and description:
            Project.objects.create(title=title, description=description)
            return redirect('project_list')
    return render(request, 'tracker/create_project.html')

@login_required
def send_announcement(request):
    if not request.user.is_superuser:
        return redirect('project_list')
        
    if request.method == 'POST':
        message = request.POST.get('message')
        recipient_id = request.POST.get('recipient') # Grab chosen team member ID
        
        recipient = None
        if recipient_id: # If not blank, target that specific profile
            recipient = get_object_or_404(User, id=recipient_id)
            
        if message:
            Notification.objects.create(message=message, recipient=recipient)
            return redirect('project_list')
            
    # Send all team profiles down to the template dropdown list
    users = User.objects.all().order_by('username')
    return render(request, 'tracker/send_announcement.html', {'users': users})