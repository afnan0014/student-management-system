from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Department, Course, Subject
from .forms import DepartmentForm, CourseForm, SubjectForm
from django.db.models import Q

# Existing views for listing (assumed)
def department_list(request):
    query = request.GET.get('q', '')
    departments = Department.objects.filter(
        Q(name__icontains=query)
    ).order_by('name')
    return render(request, 'courses/department_list.html', {'departments': departments, 'query': query})

def course_list(request):
    query = request.GET.get('q', '')
    courses = Course.objects.filter(
        Q(name__icontains=query) | Q(department__name__icontains=query)
    ).order_by('department', 'name')
    return render(request, 'courses/course_list.html', {'courses': courses, 'query': query})

def subject_list(request):
    query = request.GET.get('q', '')
    subjects = Subject.objects.filter(
        Q(name__icontains=query) | Q(course__name__icontains=query) | Q(staff__username__icontains=query)
    ).order_by('course', 'semester', 'name')
    return render(request, 'courses/subject_list.html', {'subjects': subjects, 'query': query})

# Existing views for adding (assumed)
def add_department(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department added successfully!')
            return redirect('department_list')
    else:
        form = DepartmentForm()
    return render(request, 'courses/add_department.html', {'form': form})

def add_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course added successfully!')
            return redirect('course_list')
    else:
        form = CourseForm()
    return render(request, 'courses/add_course.html', {'form': form})

def add_subject(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject added successfully!')
            return redirect('subject_list')
    else:
        form = SubjectForm()
    return render(request, 'courses/add_subject.html', {'form': form})

# New views for editing
def edit_department(request, department_id):
    department = get_object_or_404(Department, id=department_id)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department updated successfully!')
            return redirect('department_list')
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'courses/edit_department.html', {'form': form})

def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully!')
            return redirect('course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'courses/edit_course.html', {'form': form})

def edit_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject updated successfully!')
            return redirect('subject_list')
    else:
        form = SubjectForm(instance=subject)
    return render(request, 'courses/edit_subject.html', {'form': form})

# New views for deleting
def delete_departments(request):
    if request.method == 'POST':
        department_ids = request.POST.get('department_ids', '').split(',')
        if department_ids and department_ids[0]:
            Department.objects.filter(id__in=department_ids).delete()
            messages.success(request, 'Selected departments deleted successfully!')
        else:
            messages.error(request, 'No departments selected for deletion.')
    return redirect('department_list')

def delete_courses(request):
    if request.method == 'POST':
        course_ids = request.POST.get('course_ids', '').split(',')
        if course_ids and course_ids[0]:
            Course.objects.filter(id__in=course_ids).delete()
            messages.success(request, 'Selected courses deleted successfully!')
        else:
            messages.error(request, 'No courses selected for deletion.')
    return redirect('course_list')

def delete_subjects(request):
    if request.method == 'POST':
        subject_ids = request.POST.get('subject_ids', '').split(',')
        if subject_ids and subject_ids[0]:
            Subject.objects.filter(id__in=subject_ids).delete()
            messages.success(request, 'Selected subjects deleted successfully!')
        else:
            messages.error(request, 'No subjects selected for deletion.')
    return redirect('subject_list')