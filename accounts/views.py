from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from django.contrib.auth.forms import AuthenticationForm
from .decorators import allowed_users
from .forms import CustomUserCreationForm, StudentProfileForm, StaffProfileForm, PasswordChangeForm
from .models import StudentProfile, StaffProfile, Course, Department

# Landing page view
def landing_view(request):
    if request.user.is_authenticated:
        group_name = request.user.groups.first().name if request.user.groups.exists() else None
        if group_name == 'Admin':
            return redirect('admin_dashboard')
        elif group_name == 'Staff':
            return redirect('staff_dashboard')
        elif group_name == 'Student':
            return redirect('student_dashboard')
        messages.warning(request, "User does not belong to any recognized group.")
        return redirect('login')
    return render(request, 'landing.html')

# Login view
def login_view(request):
    if request.user.is_authenticated:
        group_name = request.user.groups.first().name if request.user.groups.exists() else None
        if group_name == 'Admin':
            return redirect('admin_dashboard')
        elif group_name == 'Staff':
            return redirect('staff_dashboard')
        elif group_name == 'Student':
            return redirect('student_dashboard')
        messages.warning(request, "User does not belong to any recognized group.")
        return redirect('login')

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                group = user.groups.first().name if user.groups.exists() else None
                return redirect(f'{group.lower()}_dashboard') if group else redirect('login')
        messages.error(request, "Invalid username or password.")
    return render(request, 'login.html', {'form': form})

# Logout view
def logout_view(request):
    logout(request)
    return redirect('landing')

# My Profile View (for the offcanvas right sidebar)
@login_required
def my_profile(request):
    return render(request, 'accounts/profile.html')

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

# Add user
@login_required
@allowed_users(allowed_roles=['Admin'])
def add_user(request, role):
    student_form = StudentProfileForm(request.POST or None) if role.lower() == 'student' else None
    staff_form = StaffProfileForm(request.POST or None) if role.lower() == 'staff' else None

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid() and (not student_form or student_form.is_valid()) and (not staff_form or staff_form.is_valid()):
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
                    StaffProfile.objects.create(
                        user=user,
                        department=staff_form.cleaned_data.get('department'),
                        course=staff_form.cleaned_data.get('course')
                    )

                messages.success(request, f"{role.capitalize()} account created for {user.username}")
                return redirect('view_users_by_role', role=role.lower())
            except Group.DoesNotExist:
                messages.error(request, f"Group '{role}' does not exist.")
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

# Check if user is admin
def is_admin(user):
    return user.is_authenticated and user.groups.filter(name='Admin').exists()

# View users by role
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

# Delete a user
@login_required
@user_passes_test(is_admin)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, "User deleted successfully.")
    return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard'))

# Change user password (by Admin)
@login_required
@user_passes_test(is_admin)
def change_password(request, user_id):
    user = get_object_or_404(User, id=user_id)
    form = PasswordChangeForm(user=user, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, '✅ Password changed successfully!')
        return redirect('view_users_by_role', role='Staff')
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

# Student Profile Management
@login_required
@user_passes_test(is_admin)
def student_profile(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    student_profile = get_object_or_404(StudentProfile, user=profile_user)

    all_courses = Course.objects.all()
    all_departments = Department.objects.all()

    if request.method == 'POST':
        course_id = request.POST.get('course')
        department_id = request.POST.get('department')
        student_profile.batch_number = request.POST.get('batch_number')

        student_profile.course = get_object_or_404(Course, id=course_id) if course_id else None
        student_profile.department = get_object_or_404(Department, id=department_id) if department_id else None

        student_profile.save()
        messages.success(request, "Student profile updated successfully.")
        return redirect('student_profile', user_id=user_id)

    return render(request, 'accounts/student_profile.html', {
        'profile_user': profile_user,
        'student_profile': student_profile,
        'all_courses': all_courses,
        'all_departments': all_departments,
    })

# Staff Profile View (Admin-only)
@login_required
@user_passes_test(is_admin)
def staff_profile(request, user_id):
    profile_user = get_object_or_404(User, id=user_id, groups__name='Staff')
    staff_profile = get_object_or_404(StaffProfile, user=profile_user)
    return render(request, 'accounts/staff_profile.html', {
        'profile_user': profile_user,
        'staff_profile': staff_profile,
    })
