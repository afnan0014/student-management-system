from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from django.contrib.auth.forms import AuthenticationForm
from .decorators import allowed_users
from .forms import CustomUserCreationForm, StudentProfileForm, StaffProfileForm, PasswordChangeForm
from .models import StudentProfile, StaffProfile



# Redirect to login
def home_redirect(request):
    return redirect('login')

# Login view
def login_view(request):
    if request.user.is_authenticated:
        # Redirect based on user group
        group_name = request.user.groups.first().name if request.user.groups.exists() else None
        if group_name == 'Admin':
            return redirect('admin_dashboard')
        elif group_name == 'Staff':
            return redirect('staff_dashboard')
        elif group_name == 'Student':
            return redirect('student_dashboard')
        else:
            # If user has no group, redirect to login (or handle as needed)
            messages.warning(request, "User does not belong to any recognized group.")
            return redirect('login')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                # Redirect to dashboard after login
                group_name = user.groups.first().name if user.groups.exists() else None
                if group_name == 'Admin':
                    return redirect('admin_dashboard')
                elif group_name == 'Staff':
                    return redirect('staff_dashboard')
                elif group_name == 'Student':
                    return redirect('student_dashboard')
                else:
                    messages.warning(request, "User does not belong to any recognized group.")
                    return redirect('login')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})

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
    student_form = None
    staff_form = None

    if role.lower() == 'student':
        student_form = StudentProfileForm(request.POST or None)
    elif role.lower() == 'staff':
        staff_form = StaffProfileForm(request.POST or None)

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid() and (role.lower() != 'student' or student_form.is_valid()) and (role.lower() != 'staff' or staff_form.is_valid()):
            user = form.save()
            try:
                group = Group.objects.get(name=role.capitalize())
                user.groups.add(group)

                if role.lower() == 'student':
                    StudentProfile.objects.create(
                        user=user,
                        course=student_form.cleaned_data['course'],
                        department=student_form.cleaned_data['department'],
                        batch_number=student_form.cleaned_data['batch_number']
                    )
                elif role.lower() == 'staff':
                    # Create StaffProfile with optional department and course
                    StaffProfile.objects.create(
                        user=user,
                        department=staff_form.cleaned_data['department'] or None,
                        course=staff_form.cleaned_data['course'] or None
                    )

                messages.success(request, f"{role.capitalize()} account created for {user.username}")
                return redirect('view_users_by_role', role=role.lower())
            except Group.DoesNotExist:
                messages.error(request, f"Group '{role.capitalize()}' does not exist.")
                user.delete()
        else:
            messages.error(request, "Form is invalid. Please check the input.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/add_user.html', {
        'form': form,
        'role': role.capitalize(),
        'student_form': student_form,
        'staff_form': staff_form,
    })

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
        users = users.filter(models.Q(username__icontains=query))

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
def change_password(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = PasswordChangeForm(user=user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Password changed successfully!')
            return redirect('view_users_by_role', role='Staff')  # or wherever
    else:
        form = PasswordChangeForm(user=user)

    return render(request, 'accounts/change_user_password.html', {'form': form})


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

@login_required
@user_passes_test(is_admin)
def student_profile(request, user_id):
    profile_user = get_object_or_404(User, id=user_id, groups__name='Student')
    student_profile = get_object_or_404(StudentProfile, user=profile_user)
    return render(request, 'accounts/student_profile.html', {
        'profile_user': profile_user,
        'student_profile': student_profile,
    })

@login_required
@user_passes_test(is_admin)
def staff_profile(request, user_id):
    profile_user = get_object_or_404(User, id=user_id, groups__name='Staff')
    staff_profile = get_object_or_404(StaffProfile, user=profile_user)
    return render(request, 'accounts/staff_profile.html', {
        'profile_user': profile_user,
        'staff_profile': staff_profile,
    })
