from django.shortcuts import render
from accounts.decorators import allowed_users
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth import logout

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




