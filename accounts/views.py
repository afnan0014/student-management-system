from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from .decorators import allowed_users
from .forms import CustomUserCreationForm

# Redirect to login
def home_redirect(request):
    return redirect('login')

# Login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            group = user.groups.first().name

            if group == 'Admin':
                return redirect('admin_dashboard')
            elif group == 'Staff':
                return redirect('staff_dashboard')
            elif group == 'Student':
                return redirect('student_dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'login.html')

# Dashboards
@login_required
@allowed_users(allowed_roles=['Admin'])
def admin_dashboard(request):
    return render(request, 'dashboard/admin_dashboard.html')

@login_required
@allowed_users(allowed_roles=['Staff'])
def staff_dashboard(request):
    return render(request, 'dashboard/staff_dashboard.html')

@login_required
@allowed_users(allowed_roles=['Student'])
def student_dashboard(request):
    return render(request, 'dashboard/student_dashboard.html')

# Logout
def logout_view(request):
    logout(request)
    return redirect('login')

# Add user
@login_required
@allowed_users(allowed_roles=['Admin'])
def add_user(request, role):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Password already hashed by UserCreationForm
            try:
                group = Group.objects.get(name=role.capitalize())
                user.groups.add(group)
                messages.success(request, f"{role.capitalize()} account created for {user.username}")
                return redirect('view_users_by_role', role=role.lower())
            except Group.DoesNotExist:
                messages.error(request, f"Group '{role.capitalize()}' does not exist.")
                user.delete()  # Clean up if group assignment fails
        else:
            messages.error(request, "Form is invalid. Please check the input.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/add_user.html', {'form': form, 'role': role.capitalize()})

# Role check
def is_admin(user):
    return user.is_authenticated and user.groups.filter(name='Admin').exists()

# View users by role with search
@login_required
@user_passes_test(is_admin)
def view_users_by_role(request, role):
    query = request.GET.get('q', '').strip()
    users = User.objects.filter(groups__name=role.capitalize())

    if query:
        users = users.filter(models.Q(username__icontains=query) | models.Q(email__icontains=query))

    return render(request, 'accounts/user_list.html', {
        'users': users,
        'role': role.capitalize(),
        'query': query,
    })

# Delete user
@login_required
@user_passes_test(is_admin)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, "User deleted successfully.")
    return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard'))

# Change user password
@login_required
@user_passes_test(is_admin)
def change_user_password(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        user.set_password(new_password)
        user.save()
        messages.success(request, "Password updated successfully.")
        return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard'))

    return render(request, 'accounts/change_user_password.html', {'user': user})

# Bulk delete users
@login_required
@user_passes_test(is_admin)
def bulk_delete_users(request):
    if request.method == 'POST':
        ids = request.POST.getlist('selected_users')
        if ids:
            count, _ = User.objects.filter(id__in=ids).delete()
            messages.success(request, f"Deleted {count} user{'s' if count != 1 else ''}.")
        else:
            messages.warning(request, "No users selected for deletion.")
    return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard'))