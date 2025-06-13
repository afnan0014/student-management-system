from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Department, Course
from .forms import DepartmentForm, CourseForm
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

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CourseForm, SubjectFormSet
from .models import Subject

def add_course(request):
    if request.method == 'POST':
        course_form = CourseForm(request.POST)
        subject_formset = SubjectFormSet(request.POST, queryset=Subject.objects.none())

        if course_form.is_valid() and subject_formset.is_valid():
            course = course_form.save()
            for subject_form in subject_formset:
                if subject_form.cleaned_data and not subject_form.cleaned_data.get('DELETE'):
                    subject = subject_form.save(commit=False)
                    subject.course = course
                    subject.save()

            messages.success(request, '✅ Course and subjects added successfully!')
            return redirect('course_list')
        else:
            messages.error(request, '❌ Please correct the errors below.')
    else:
        course_form = CourseForm()
        subject_formset = SubjectFormSet(queryset=Subject.objects.none())

    return render(request, 'courses/add_course.html', {
        'form': course_form,
        'subject_formset': subject_formset
    })




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
    subject_qs = Subject.objects.filter(course=course)

    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        subject_formset = SubjectFormSet(request.POST, queryset=subject_qs)

        if form.is_valid() and subject_formset.is_valid():
            # Save course
            course = form.save()

            # Save or add new subjects
            subject_instances = subject_formset.save(commit=False)
            for subject in subject_instances:
                subject.course = course
                subject.save()

            # Delete subjects marked for deletion
            for obj in subject_formset.deleted_objects:
                obj.delete()

            messages.success(request, '✅ Course and subjects updated successfully!')
            return redirect('course_list')
        else:
            messages.error(request, '❌ Please correct the errors below.')
    else:
        form = CourseForm(instance=course)
        subject_formset = SubjectFormSet(queryset=subject_qs)

    return render(request, 'courses/edit_course.html', {
        'form': form,
        'subject_formset': subject_formset,
    })




   

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


def course_subjects(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    subjects = Subject.objects.filter(course=course)

    return render(request, 'courses/view_subjects.html', {
        'course': course,
        'subjects': subjects
    })

from .models import Subject

def view_subjects_by_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    subjects = Subject.objects.filter(course=course)
    return render(request, 'courses/subject_list.html', {
        'course': course,
        'subjects': subjects
    })