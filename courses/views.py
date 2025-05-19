
# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import DepartmentForm, CourseForm, SubjectForm

@login_required
def add_department(request):
    form = DepartmentForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('add_department')
    return render(request, 'courses/add_department.html', {'form': form})

@login_required
def add_course(request):
    form = CourseForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('add_course')
    return render(request, 'courses/add_course.html', {'form': form})

@login_required
def add_subject(request):
    form = SubjectForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('add_subject')
    return render(request, 'courses/add_subject.html', {'form': form})
