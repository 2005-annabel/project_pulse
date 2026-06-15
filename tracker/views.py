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
        project_id = request.POST.get('project_id')
        
        can_post = True
        if not request.user.is_superuser:
            last_update = ProgressUpdate.objects.filter(user=request.user).last()
            if last_update and not last_update.can_update:
                can_post = False

        if can_post and task_done and details and project_id:
            project_instance = get_object_or_404(Project, id=project_id)
            ProgressUpdate.objects.create(
                user=request.user,
                project=project_instance,
                task_done=task_done,
                details=details
            )
            return redirect('project_list')

    # --- SEPARATE ACTIVE PIPELINES VS ARCHIVED HISTORY ---
    active_projects = Project.objects.filter(is_completed=False)
    completed_projects = Project.objects.filter(is_completed=True)
    
    if request.user.is_superuser:
        # Superuser sees active updates linked only to active projects on the main feed
        updates = ProgressUpdate.objects.filter(project__is_completed=False).order_by('-created_at')
        # Historical updates are routed to the history log
        archived_updates = ProgressUpdate.objects.filter(project__is_completed=True).order_by('-created_at')
    else:
        # Regular users see their own updates for active projects
        updates = ProgressUpdate.objects.filter(user=request.user, project__is_completed=False).order_by('-created_at')
        archived_updates = ProgressUpdate.objects.filter(user=request.user, project__is_completed=True).order_by('-created_at')
    
    alerts = Notification.objects.filter(
        Q(recipient=request.user) | Q(recipient__isnull=True)
    ).order_by('-created_at')
    
    return render(request, 'tracker/project_list.html', {
        'projects': active_projects,              # Main feed projects
        'completed_projects': completed_projects, # History tab projects
        'updates': updates,                       # Main feed logs
        'archived_updates': archived_updates,     # History tab logs
        'alerts': alerts
    })

@login_required
def toggle_project_status(request, pk):
    """View to allow superusers to flip a project between Active and Completed"""
    if request.user.is_superuser:
        project = get_object_or_404(Project, pk=pk)
        project.is_completed = not project.is_completed
        project.save()
    return redirect('project_list')

# --- KEEP ALL OTHER AUTH/PERMISSION LOGIC BELOW EXACTLY THE SAME ---
def signup_view(request):
    if request.user.is_authenticated: return redirect('project_list')
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
    if update.user != request.user and not request.user.is_superuser: return redirect('project_list')
    if not update.can_update and not request.user.is_superuser: return redirect('project_list')
    if request.method == 'POST':
        update.task_done = request.POST.get('task_done')
        update.details = request.POST.get('details')
        update.save()
        return redirect('project_list')
    return render(request, 'tracker/edit_progress.html', {'update': update})

@login_required
def delete_progress(request, pk):
    update = get_object_or_404(ProgressUpdate, pk=pk)
    if not update.can_delete and not request.user.is_superuser: return redirect('project_list')
    if update.user == request.user or request.user.is_superuser: update.delete()
    return redirect('project_list')

@login_required
def dismiss_notification(request, pk):
    alert = get_object_or_404(Notification, pk=pk)
    if alert.recipient == request.user or request.user.is_superuser or alert.recipient is None: alert.delete()
    return redirect('project_list')

@login_required
def toggle_update_permission(request, pk):
    if request.user.is_superuser:
        update = get_object_or_404(ProgressUpdate, pk=pk)
        ProgressUpdate.objects.filter(user=update.user).update(can_update=not update.can_update)
    return redirect('project_list')

@login_required
def toggle_delete_permission(request, pk):
    if request.user.is_superuser:
        update = get_object_or_404(ProgressUpdate, pk=pk)
        ProgressUpdate.objects.filter(user=update.user).update(can_delete=not update.can_delete)
    return redirect('project_list')

@login_required
def create_main_project(request):
    if not request.user.is_superuser: return redirect('project_list')
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        if title and description:
            Project.objects.create(title=title, description=description)
            return redirect('project_list')
    return render(request, 'tracker/create_project.html')

@login_required
def send_announcement(request):
    if not request.user.is_superuser: return redirect('project_list')
    if request.method == 'POST':
        message = request.POST.get('message')
        recipient_id = request.POST.get('recipient')
        recipient = None
        if recipient_id: recipient = get_object_or_404(User, id=recipient_id)
        if message:
            Notification.objects.create(message=message, recipient=recipient)
            return redirect('project_list')
    users = User.objects.all().order_by('username')
    return render(request, 'tracker/send_announcement.html', {'users': users})