from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Project, ProgressUpdate, Notification
from .forms import ProjectForm, ProgressForm, NotificationForm, SignUpForm

# --- AUTH SYSTEM ---
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('project_list')
    else: form = SignUpForm()
    return render(request, 'tracker/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('project_list')
    else: form = AuthenticationForm()
    return render(request, 'tracker/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')


# --- ARCHITECTURE CONTROLLER VIEWS ---

@login_required
def project_list(request):
    main_projects = Project.objects.all().order_by('-id')
    
    if request.user.is_superuser:
        all_updates = ProgressUpdate.objects.all().order_by('-updated_at')
        # Supervisors see all notifications to audit read receipts
        alerts = Notification.objects.all().order_by('-id')
    else:
        all_updates = ProgressUpdate.objects.filter(user=request.user).order_by('-updated_at')
        # Regular users only see alerts they haven't acknowledged/ticked yet
        alerts = Notification.objects.filter(
            Q(recipient=request.user) | Q(recipient__isnull=True)
        ).exclude(acknowledged_by=request.user).order_by('-id')

    return render(request, 'tracker/project_list.html', {
        'projects': main_projects,
        'updates': all_updates,
        'alerts': alerts
    })

# NEW VIEW: Handles clicking the tick button
@login_required
def dismiss_notification(request, pk):
    alert = get_object_or_404(Notification, pk=pk)
    alert.acknowledged_by.add(request.user)
    return redirect('project_list')

@login_required
def create_main_project(request):
    if not request.user.is_superuser: return redirect('project_list')
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('project_list')
    else: form = ProjectForm()
    return render(request, 'tracker/project_form.html', {'form': form, 'title': 'Create Corporate Main Project'})

@login_required
def log_progress(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk)
    if request.method == 'POST':
        form = ProgressForm(request.POST)
        if form.is_valid():
            update = form.save(commit=False)
            update.project = project
            update.user = request.user
            update.save()
            return redirect('project_list')
    else: form = ProgressForm()
    return render(request, 'tracker/project_form.html', {'form': form, 'title': f'Log Progress for: {project.title}'})

@login_required
def edit_progress(request, pk):
    if request.user.is_superuser:
        update = get_object_or_404(ProgressUpdate, pk=pk)
    else:
        # Check ownership and whether editing is currently permitted by the manager
        update = get_object_or_404(ProgressUpdate, pk=pk, user=request.user)
        if not update.can_edit:
            return render(request, 'tracker/project_list.html', {'error': 'Your editing access has been revoked by the supervisor!'})

    if request.method == 'POST':
        form = ProgressForm(request.POST, instance=update)
        if form.is_valid():
            form.save()
            return redirect('project_list')
    else: form = ProgressForm(instance=update)
    return render(request, 'tracker/project_form.html', {'form': form, 'title': 'Modify Progress Log Entry'})

@login_required
def delete_progress(request, pk):
    # Only supervisors get access to the permanent delete function
    if not request.user.is_superuser: return redirect('project_list')
    update = get_object_or_404(ProgressUpdate, pk=pk)
    if request.method == 'POST':
        update.delete()
        return redirect('project_list')
    return render(request, 'tracker/project_confirm_delete.html', {'project': update})


# --- SUPERUSER CONTROLS ---

@login_required
def send_announcement(request):
    if not request.user.is_superuser: return redirect('project_list')
    if request.method == 'POST':
        form = NotificationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('project_list')
    else: form = NotificationForm()
    return render(request, 'tracker/send_notification.html', {'form': form})

@login_required
def toggle_permission(request, pk):
    if not request.user.is_superuser: return redirect('project_list')
    update = get_object_or_404(ProgressUpdate, pk=pk)
    update.can_edit = not update.can_edit  # Flip the boolean switch
    update.save()
    return redirect('project_list')