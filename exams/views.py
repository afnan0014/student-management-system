from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Exam, Mark, Subject
from .forms import MarkFormSet
from accounts.models import StudentProfile, StaffProfile
import csv
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from courses.models import Course, Subject

@login_required
def mark_entry_view(request, exam_id):
    staff_profile = getattr(request.user, 'staff_profile', None)

    if not staff_profile or not staff_profile.course:
        messages.error(request, "You are not assigned to a course.")
        return redirect('course_list')

    exam = get_object_or_404(Exam, id=exam_id, course=staff_profile.course)
    students = StudentProfile.objects.filter(course=staff_profile.course)
    subjects = Subject.objects.filter(course=staff_profile.course)

    if request.method == 'GET':
        for student in students:
            for subject in subjects:
                Mark.objects.get_or_create(
                    student=student,
                    exam=exam,
                    subject=subject,
                    defaults={'marks_obtained': 0}
                )
        formset = MarkFormSet(queryset=Mark.objects.filter(
            exam=exam,
            student__course=staff_profile.course
        ))
        return render(request, 'exams/mark_entry.html', {
            'formset': formset,
            'exam': exam
        })

    else:  # POST
        formset = MarkFormSet(
            request.POST,
            queryset=Mark.objects.filter(
                exam=exam,
                student__course=staff_profile.course
            )
        )
        if formset.is_valid():
            formset.save()
            messages.success(request, "Marks saved successfully!")
            return redirect('course_list')
        else:
            messages.error(request, "Error saving marks.")
            return render(request, 'exams/mark_entry.html', {
                'formset': formset,
                'exam': exam
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

    return render(request, 'exams/report_card.html', {
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
    return render(request, 'exams/export_results.html', {
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
