from django.shortcuts import render, redirect
from .models import Attendance
from courses.models import Subject
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import datetime

@login_required
def mark_attendance(request):
    staff_user = request.user
    subjects = Subject.objects.filter(staff=staff_user)

    if request.method == 'POST':
        subject_id = request.POST.get('subject')
        date = request.POST.get('date')
        selected_subject = Subject.objects.get(id=subject_id)
        student_ids = request.POST.getlist('student_ids')
        statuses = request.POST.getlist('statuses')

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
