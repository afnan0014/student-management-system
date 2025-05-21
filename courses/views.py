from django.shortcuts import render, redirect
from .models import Department, Course, Subject
from .forms import DepartmentForm, CourseForm, SubjectForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def add_department(request):
    form = DepartmentForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Department added successfully.")
        return redirect('department_list')
    return render(request, 'courses/add_department.html', {'form': form})

@login_required
def department_list(request):
    departments = Department.objects.all()
    return render(request, 'courses/department_list.html', {'departments': departments})


@login_required
def add_course(request):
    form = CourseForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Course added successfully.")
        return redirect('course_list')
    return render(request, 'courses/add_course.html', {'form': form})

@login_required
def course_list(request):
    courses = Course.objects.select_related('department')
    return render(request, 'courses/course_list.html', {'courses': courses})


@login_required
def add_subject(request):
    form = SubjectForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Subject added successfully.")
        return redirect('subject_list')
    return render(request, 'courses/add_subject.html', {'form': form})

@login_required
def subject_list(request):
    subjects = Subject.objects.select_related('course', 'staff')
    return render(request, 'courses/subject_list.html', {'subjects': subjects})
