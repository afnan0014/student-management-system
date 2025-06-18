from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
import json
from datetime import date
from collections import Counter

from accounts.models import StudentProfile, StaffProfile
from attendance.models import Attendance
from exams.models import Exam, Result, Mark
from timetable.models import TimetableEntry
from courses.models import Course
from assignments.models import Assignment, Submission


# -------------------- Admin Dashboard --------------------
@login_required
def admin_dashboard(request):
    total_students = StudentProfile.objects.count()
    total_staff = StaffProfile.objects.count()
    total_exams = Exam.objects.count()

    attendance_present = Attendance.objects.filter(status='Present').count()
    total_attendance = Attendance.objects.count()
    attendance_rate = (attendance_present / max(total_attendance, 1)) * 100

    # Chart Data
    bar_data = StudentProfile.objects.values('course__name').annotate(count=Count('attendance')).order_by('course__name')
    pie_data = StudentProfile.objects.values('course__department__name').annotate(count=Count('id'))


    context = {
        'total_students': total_students,
        'total_staff': total_staff,
        'attendance_rate': round(attendance_rate, 2),
        'total_exams': total_exams,
        'bar_data': list(bar_data),
        'pie_data': list(pie_data),
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def staff_dashboard(request):
    user = request.user

    try:
        staff = StaffProfile.objects.get(user=user)
    except StaffProfile.DoesNotExist:
        return render(request, "errors/403.html", status=403)

    courses = Course.objects.filter(assigned_staff=user)
    courses_handled = courses.count()

    total_students = StudentProfile.objects.filter(course__in=courses).count()
    attendance_taken = Attendance.objects.filter(course__in=courses, student__course__in=courses).values('date').distinct().count()
    today = date.today()
    upcoming_exams = Exam.objects.filter(course__in=courses, date__gte=today).count()

    recent_attendance = Attendance.objects.filter(course__in=courses).values_list('date', flat=True)
    date_counts = Counter(recent_attendance)
    sorted_dates = sorted(date_counts.keys())[-7:]

    attendance_chart_labels = [d.strftime('%Y-%m-%d') for d in sorted_dates]
    attendance_chart_values = [date_counts[d] for d in sorted_dates]

    return render(request, 'dashboard/staff_dashboard.html', {
        'user': user,
        'courses_handled': courses_handled,
        'total_students': total_students,
        'attendance_taken': attendance_taken,
        'upcoming_exams': upcoming_exams,
        'attendance_chart_labels': attendance_chart_labels,
        'attendance_chart_values': attendance_chart_values,
    })


@login_required
def student_dashboard(request):
    try:
        student = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        return render(request, "dashboard/no_profile.html")

    today = timezone.now().date()

    total_classes = Attendance.objects.filter(student=student).count()
    present_classes = Attendance.objects.filter(student=student, status="Present").count()
    attendance_percentage = (present_classes / max(total_classes, 1)) * 100

    todays_classes = TimetableEntry.objects.filter(
        day=today.strftime("%A"),
        course=student.course
    ).order_by("period_number")

    # Exams
    exams_appeared = Mark.objects.filter(student=student).values('exam').distinct().count()

    # Attendance pie chart
    attendance_data = Attendance.objects.filter(student=student).values('status').annotate(count=Count('id'))
    attendance_labels = [entry['status'] for entry in attendance_data]
    attendance_counts = [entry['count'] for entry in attendance_data]

    # Marks chart
    marks_qs = Mark.objects.filter(student=student)
    subject_marks = marks_qs.values_list('subject__name', 'marks_obtained')
    subject_labels = [subject for subject, _ in subject_marks]
    obtained_marks = [mark for _, mark in subject_marks]

    # Assignments
    assignments = Assignment.objects.filter(students=request.user)
    total_assignments = assignments.count()
    upcoming_assignments = assignments.filter(deadline__gte=timezone.now()).count()

    submitted_assignments = Submission.objects.filter(student=request.user).values('assignment').distinct().count()
    pending_assignments = total_assignments - submitted_assignments

    context = {
        "my_course": student.course.name,
        "todays_classes": todays_classes,
        "my_attendance": round(attendance_percentage, 2),
        "exams_appeared": exams_appeared,
        "attendance_labels": json.dumps(attendance_labels),
        "attendance_counts": json.dumps(attendance_counts),
        "subject_labels": json.dumps(subject_labels),
        "obtained_marks": json.dumps(obtained_marks),
        "total_assignments": total_assignments,
        "upcoming_assignments": upcoming_assignments,
        "submitted_assignments": submitted_assignments,
        "pending_assignments": pending_assignments,
    }

    return render(request, "dashboard/student_dashboard.html", context)
