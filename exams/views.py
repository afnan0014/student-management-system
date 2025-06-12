# exams/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Exam, Mark, Subject, Result
from .forms import MarkForm, ExamForm
from accounts.models import StudentProfile, StaffProfile
import csv
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from courses.models import Course, Subject
from django.forms import modelformset_factory
from django.db.models import Q
from notifications.utils import notify_users  # Import the notification utility

@login_required
def staff_mark_entry_spreadsheet(request):
    staff_profile = getattr(request.user, 'staff_profile', None)
    if not staff_profile or not staff_profile.course:
        messages.error(request, "You are not assigned to a course.")
        return redirect('staff_dashboard')

    exams = Exam.objects
    filter(course=staff_profile.course)
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
            instances = formset.save()
            for mark in instances:
                # Send notification to student
                notify_users('marks_added', request.user, course=staff_profile.course, mark=mark)
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
        return redirect('home')

    exam_filter = request.GET.get('exam')
    subject_filter = request.GET.get('subject')
    status_filter = request.GET.get('status')

    marks_qs = Mark.objects.filter(student=student_profile).select_related('exam', 'subject')

    if exam_filter:
        marks_qs = marks_qs.filter(exam__id=exam_filter)
    if subject_filter:
        marks_qs = marks_qs.filter(subject__id=subject_filter)

    def get_grade(m):
        if m >= 90: return 'A+'
        elif m >= 80: return 'A'
        elif m >= 70: return 'B+'
        elif m >= 60: return 'B'
        elif m >= 50: return 'C'
        return 'F'

    marks = []
    total_passed = total_failed = 0

    for mark in marks_qs:
        grade = get_grade(mark.marks_obtained)
        status = "Passed" if mark.marks_obtained >= 50 else "Failed"

        if status_filter == 'pass' and status != "Passed":
            continue
        if status_filter == 'fail' and status != "Failed":
            continue

        mark.grade = grade
        mark.status = status
        marks.append(mark)

        if status == "Passed":
            total_passed += 1
        else:
            total_failed += 1

    grouped = {}
    for mark in marks:
        exam = mark.exam
        exam_key = (exam.id, exam.name, exam.date)
        if exam_key not in grouped:
            grouped[exam_key] = {
                'name': exam.name,
                'date': exam.date,
                'marks': [],
                'total_max': 0,
                'total_obtained': 0,
                'pass_count': 0,
                'fail_count': 0
            }

        grouped[exam_key]['marks'].append(mark)
        grouped[exam_key]['total_max'] += 100
        grouped[exam_key]['total_obtained'] += mark.marks_obtained
        if mark.status == 'Passed':
            grouped[exam_key]['pass_count'] += 1
        else:
            grouped[exam_key]['fail_count'] += 1

    grouped_results = list(grouped.values())

    exams = Exam.objects.filter(mark__student=student_profile).distinct()
    subjects = marks_qs.values_list('subject__id', 'subject__name').distinct()

    return render(request, 'exam/report_card.html', {
        'grouped_results': grouped_results,
        'exams': exams,
        'subjects': subjects,
        'selected_exam': exam_filter,
        'selected_subject': subject_filter,
        'selected_status': status_filter,
        'total_passed': total_passed,
        'total_failed': total_failed,
    })

@staff_member_required
def export_results_view(request):
    course_id = request.GET.get('course')
    staff_id = request.GET.get('staff')
    subject_id = request.GET.get('subject')
    exam_id = request.GET.get('exam')

    marks = Mark.objects.select_related('student__user', 'exam', 'subject', 'student__course')

    if course_id:
        marks = marks.filter(student__course_id=course_id)
    if staff_id:
        marks = marks.filter(exam__course__staff__user_id=staff_id)
    if subject_id:
        marks = marks.filter(subject_id=subject_id)
    if exam_id:
        marks = marks.filter(exam_id=exam_id)

    def calculate_grade(mark):
        if mark >= 90: return 'A+'
        elif mark >= 80: return 'A'
        elif mark >= 70: return 'B+'
        elif mark >= 60: return 'B'
        elif mark >= 50: return 'C'
        else: return 'F'

    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="exam_results.csv"'
        writer = csv.writer(response)
        writer.writerow(['Student', 'Course', 'Exam', 'Subject', 'Max Marks', 'Obtained Marks', 'Grade', 'Status'])

        for mark in marks:
            obtained = mark.marks_obtained
            grade = calculate_grade(obtained)
            status = 'Passed' if obtained >= 50 else 'Failed'

            writer.writerow([
                mark.student.user.get_full_name(),
                mark.student.course.name if mark.student.course else 'N/A',
                mark.exam.name,
                mark.subject.name,
                100,
                obtained,
                grade,
                status,
            ])
        return response

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
        },
        'calculate_grade': calculate_grade
    })

def create_exam(request):
    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.created_by = request.user
            exam.save()

            course = exam.course
            subjects = Subject.objects.filter(course=course)
            students = StudentProfile.objects.filter(course=course)
            staff = StaffProfile.objects.filter(course=course)

            # Send notification to staff and students
            notify_users('exam_added', request.user, course=course, exam=exam)

            messages.success(request, f"✅ Exam '{exam.name}' created and linked to {course.name}, its students, subjects and staff.")
            return redirect('exam_list')
    else:
        form = ExamForm()

    return render(request, 'exam/create_exam.html', {'form': form})

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

def delete_exams(request):
    if request.method == 'POST':
        ids = request.POST.get('exam_ids', '').split(',')
        if ids:
            Exam.objects.filter(id__in=ids).delete()
            messages.success(request, "✅ Selected exams deleted successfully.")
    return redirect('exam_list')