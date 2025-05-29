from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Exam, Mark, Subject
from .forms import MarkForm
from accounts.models import StudentProfile, StaffProfile
import csv
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from courses.models import Course, Subject
from .forms import ExamForm
from django.forms import modelformset_factory

@login_required
def staff_mark_entry_spreadsheet(request):
    staff_profile = getattr(request.user, 'staff_profile', None)
    if not staff_profile or not staff_profile.course:
        messages.error(request, "You are not assigned to a course.")
        return redirect('staff_dashboard')

    exams = Exam.objects.filter(course=staff_profile.course)
    subjects = Subject.objects.filter(course=staff_profile.course)
    students = StudentProfile.objects.filter(course=staff_profile.course)

    exam_id = request.GET.get('exam')
    subject_id = request.GET.get('subject')

    marks = Mark.objects.none()
    selected_exam = None
    selected_subject = None

    if exam_id and subject_id:
        selected_exam = get_object_or_404(Exam, id=exam_id)
        selected_subject = get_object_or_404(Subject, id=subject_id)

        # Ensure marks exist or create them
        for student in students:
            Mark.objects.get_or_create(
                student=student,
                exam=selected_exam,
                subject=selected_subject,
                defaults={'marks_obtained': 0}
            )

            marks = Mark.objects.select_related('student__user').filter(
                exam=selected_exam,
                subject=selected_subject,
                student__course=staff_profile.course
            )


    MarkFormSet = modelformset_factory(Mark, form=MarkForm, extra=0)

    if request.method == 'POST':
        formset = MarkFormSet(request.POST, queryset=marks)
        if formset.is_valid():
            formset.save()
            messages.success(request, "Marks submitted successfully!")
            return redirect('staff_mark_entry_spreadsheet')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        formset = MarkFormSet(queryset=marks)

    return render(request, 'exam/staff_mark_entry.html', {
        'formset': formset,
        'exams': exams,
        'subjects': subjects,
        'selected_exam': exam_id,
        'selected_subject': subject_id,
    })

@login_required
def report_card_view(request):
    user = request.user
    try:
        student_profile = user.student_profile
    except StudentProfile.DoesNotExist:
        messages.error(request, "You are not a student.")
        return redirect('home')  # Or a dedicated "not allowed" page

    # Base queryset
    marks = Mark.objects.filter(student=student_profile).select_related('exam', 'subject')

    # Filtering
    exam_filter = request.GET.get('exam')
    subject_filter = request.GET.get('subject')
    grade_filter = request.GET.get('grade')

    if exam_filter:
        marks = marks.filter(exam__id=exam_filter)
    if subject_filter:
        marks = marks.filter(subject__id=subject_filter)
    if grade_filter:
        marks = marks.filter(student_result_grade=grade_filter)

    # Unique dropdown options for filtering
    exams = Exam.objects.filter(mark__student=student_profile).distinct()
    subjects = marks.values_list('subject__id', 'subject__name').distinct()
    
    # Assuming `student_result_grade` is stored directly in the Mark model
    grades = marks.values_list('student_result_grade', flat=True).distinct()

    return render(request, 'exam/report_card.html', {
        'marks': marks,
        'exams': exams,
        'subjects': subjects,
        'grades': grades,
        'selected_exam': exam_filter,
        'selected_subject': subject_filter,
        'selected_grade': grade_filter,
    })

@staff_member_required
def export_results_view(request):
    # Filter inputs
    course_id = request.GET.get('course')
    staff_id = request.GET.get('staff')
    subject_id = request.GET.get('subject')
    exam_id = request.GET.get('exam')

    # Query base
    marks = Mark.objects.select_related('student__user', 'exam', 'subject', 'student__course')

    if course_id:
        marks = marks.filter(student__course_id=course_id)
    if staff_id:
        marks = marks.filter(exam__course__staff__user_id=staff_id)
    if subject_id:
        marks = marks.filter(subject_id=subject_id)
    if exam_id:
        marks = marks.filter(exam_id=exam_id)

    # Export to CSV
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="exam_results.csv"'
        writer = csv.writer(response)
        writer.writerow(['Student', 'Course', 'Exam', 'Subject', 'Marks'])

        for mark in marks:
            writer.writerow([
                mark.student.user.get_full_name(),
                mark.student.course.name if mark.student.course else 'N/A',
                mark.exam.name,
                mark.subject.name,
                mark.marks_obtained,
            ])
        return response

    # Render HTML for filtering
    return render(request, 'exam/export_results.html', {
        'marks': marks,
        'courses': Course.objects.all(),
        'staffs': StaffProfile.objects.select_related('user'),
        'subjects': Subject.objects.all(),
        'exams': Exam.objects.all(),
        'selected': {
            'course': course_id,
            'staff': staff_id,
            'subject': subject_id,
            'exam': exam_id,
        }
    })

def create_exam(request):
    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save()

            # Fetch related course
            course = exam.course

            # Auto-assign exam to all subjects in this course
            subjects = Subject.objects.filter(course=course)
            students = StudentProfile.objects.filter(course=course)
            staff = StaffProfile.objects.filter(course=course)

            messages.success(request, f"✅ Exam '{exam.name}' created and linked to {course.name}, its students, subjects and staff.")

            return redirect('exam_list')  # change to your actual exam list view
    else:
        form = ExamForm()

    return render(request, 'exam/create_exam.html', {'form': form})


# exams/views.py

from .models import Exam
from accounts.models import StaffProfile
from courses.models import Course
from django.db.models import Q

def exam_list(request):
    exams = Exam.objects.all().select_related('course')

    query = request.GET.get('q')
    course_id = request.GET.get('course')
    staff_id = request.GET.get('staff')

    if query:
        exams = exams.filter(name__icontains=query)
    if course_id:
        exams = exams.filter(course_id=course_id)
    if staff_id:
        exams = exams.filter(course__staff__user_id=staff_id)

    courses = Course.objects.all()
    staff = StaffProfile.objects.select_related('user')

    return render(request, 'exam/exam_list.html', {
        'exams': exams,
        'courses': courses,
        'staff': staff,
    })

# exams/views.py

from django.contrib import messages
from .models import Exam

def delete_exams(request):
    if request.method == 'POST':
        ids = request.POST.get('exam_ids', '').split(',')
        if ids:
            Exam.objects.filter(id__in=ids).delete()
            messages.success(request, "✅ Selected exams deleted successfully.")
    return redirect('exam_list')

