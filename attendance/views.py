from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
import datetime

from .models import Attendance
from courses.models import Subject

# View 1: Staff — Mark Attendance
@login_required
def mark_attendance(request):
    staff_user = request.user

    # Get subjects assigned to this staff user
    subjects = Subject.objects.filter(staff=staff_user)

    if request.method == 'POST':
        subject_id = request.POST.get('subject')
        date = request.POST.get('date')
        selected_subject = Subject.objects.get(id=subject_id)

        student_ids = request.POST.getlist('student_ids')     # e.g., [1, 2, 3]
        statuses = request.POST.getlist('statuses')           # e.g., ['Present', 'Absent', 'Leave']

        # Save or update attendance records
        for student_id, status in zip(student_ids, statuses):
            Attendance.objects.update_or_create(
                date=date,
                subject=selected_subject,
                student_id=student_id,
                defaults={'status': status}
            )

        return redirect('mark_attendance')

    context = {
        'subjects': subjects,
        'today': datetime.date.today()
    }
    return render(request, 'attendance/mark_attendance.html', context)


# View 2: Student — View Attendance
@login_required
def student_attendance_view(request):
    student = request.user

    # Get all subjects related to the student's course
    subjects = Subject.objects.filter(course__in=student.course_set.all())
    subject_data = []

    for subject in subjects:
        total = Attendance.objects.filter(student=student, subject=subject).count()
        present = Attendance.objects.filter(student=student, subject=subject, status='Present').count()
        absent = Attendance.objects.filter(student=student, subject=subject, status='Absent').count()
        leave = Attendance.objects.filter(student=student, subject=subject, status='Leave').count()

        percentage = (present / total) * 100 if total > 0 else 0

        subject_data.append({
            'subject': subject.name,
            'total': total,
            'present': present,
            'absent': absent,
            'leave': leave,
            'percentage': round(percentage, 2)
        })

    return render(request, 'attendance/student_attendance.html', {
        'subject_data': subject_data
    })
