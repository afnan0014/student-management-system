from django.shortcuts import render
from accounts.decorators import allowed_users
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.models import Group
from .forms import CustomUserCreationForm







# Create your views here.
from django.shortcuts import redirect

def home_redirect(request):
    return redirect('login')



# detects the user's group and redirects them to the correct view, right after login.@login_required
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            group = user.groups.all()[0].name

            if group == 'Admin':
                return redirect('admin_dashboard')
            elif group == 'Staff':
                return redirect('staff_dashboard')
            elif group == 'Student':
                return redirect('student_dashboard')
        else:
            messages.error(request, 'Invalid credentials')

    return render(request, 'login.html')

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

def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def add_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Hash password
            user.save()

            role = form.cleaned_data['role']
            group = Group.objects.get(name=role)
            user.groups.add(group)

            messages.success(request, f"{role} account created for {user.username}")
            return redirect('admin_dashboard')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/add_user.html', {'form': form})

    from django.contrib.auth.models import User, Group
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm

@login_required
def view_users_by_role(request, role):
    users = User.objects.filter(groups__name=role)
    return render(request, 'accounts/user_list.html', {
        'users': users,
        'role': role
    })

@login_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, "User deleted successfully.")
    return redirect(request.META.get('HTTP_REFERER'))

@login_required
def change_user_password(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        user.set_password(new_password)
        user.save()
        messages.success(request, "Password updated successfully.")
        return redirect(request.META.get('HTTP_REFERER'))

    return render(request, 'accounts/change_user_password.html', {'user': user})


