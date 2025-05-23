from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.contrib.auth.models import User
from datetime import date, datetime
import csv

from courses.models import Course
from accounts.models import StudentProfile, StaffProfile
from .models import Attendance


@login_required
def mark_attendance(request):
    staff = request.user
    courses = Course.objects.filter(assigned_staff=staff)
    students = []
    selected_course = None

    course_id = request.POST.get("course") or request.GET.get("course") or ""
    selected_date = request.POST.get("date") or request.GET.get("date") or str(date.today())

    try:
        selected_date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()
    except ValueError:
        messages.error(request, "Invalid date format.")
        return redirect('mark_attendance')

    if course_id:
        try:
            selected_course = Course.objects.get(id=course_id, assigned_staff=staff)
            students = StudentProfile.objects.filter(course=selected_course)

            if request.method == "POST" and any(key.startswith("status_") for key in request.POST):
                for student in students:
                    status = request.POST.get(f'status_{student.id}')
                    if status in dict(Attendance.STATUS_CHOICES):
                        Attendance.objects.update_or_create(
                            student=student,
                            course=selected_course,
                            date=selected_date_obj,
                            defaults={'status': status}
                        )
                messages.success(request, "Attendance marked successfully.")
                return redirect(f'{request.path}?course={course_id}&date={selected_date}')
        except Course.DoesNotExist:
            messages.error(request, "Invalid course selected.")
            return redirect('mark_attendance')

    return render(request, 'attendance/mark_attendance.html', {
        'courses': courses,
        'students': students,
        'selected_course': selected_course,
        'course_id': course_id,
        'selected_date': selected_date,
    })


@login_required
def student_attendance_view(request):
    try:
        student = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('home')

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    records = Attendance.objects.filter(student=student).order_by('-date')

    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            records = records.filter(date__gte=start)
        except ValueError:
            messages.error(request, "Invalid start date format.")

    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            records = records.filter(date__lte=end)
        except ValueError:
            messages.error(request, "Invalid end date format.")

    total = records.count()
    present = records.filter(status='Present').count()
    percentage = round((present / total) * 100) if total > 0 else 0

    return render(request, 'attendance/student_attendance.html', {
        'records': records,
        'percentage': percentage,
        'start_date': start_date,
        'end_date': end_date,
    })



@staff_member_required
def admin_view_attendance(request):
    selected_date = request.GET.get('date')
    selected_staff_id = request.GET.get('staff')
    selected_course_id = request.GET.get('course')

    records = Attendance.objects.select_related('student__user', 'course').order_by('-date')

    staff_profiles = StaffProfile.objects.select_related('user').all()
    courses = Course.objects.all()

    if selected_staff_id:
        try:
            selected_staff = StaffProfile.objects.select_related('user').get(user__id=selected_staff_id)
            records = records.filter(course__assigned_staff=selected_staff.user)
        except StaffProfile.DoesNotExist:
            messages.error(request, "Selected staff member does not exist.")

    if selected_course_id:
        try:
            selected_course = Course.objects.get(id=selected_course_id)
            records = records.filter(course=selected_course)
        except Course.DoesNotExist:
            messages.error(request, "Selected course does not exist.")

    if selected_date:
        try:
            selected_date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()
            records = records.filter(date=selected_date_obj)
        except ValueError:
            messages.error(request, "Invalid date format.")

    return render(request, 'attendance/admin_view.html', {
        'records': records,
        'selected_date': selected_date,
        'selected_staff_id': selected_staff_id,
        'selected_course_id': selected_course_id,
        'staff_profiles': staff_profiles,
        'courses': courses
    })


@staff_member_required
def export_attendance_csv(request):
    selected_date = request.GET.get('date')
    selected_staff_id = request.GET.get('staff')
    selected_course_id = request.GET.get('course')

    records = Attendance.objects.select_related('student__user', 'course')

    if selected_staff_id:
        try:
            selected_staff = StaffProfile.objects.select_related('user').get(user__id=selected_staff_id)
            records = records.filter(course__assigned_staff=selected_staff.user)
        except StaffProfile.DoesNotExist:
            messages.error(request, "Selected staff member does not exist.")
            return redirect('attendance_report')

    if selected_course_id:
        try:
            selected_course = Course.objects.get(id=selected_course_id)
            records = records.filter(course=selected_course)
        except Course.DoesNotExist:
            messages.error(request, "Selected course does not exist.")
            return redirect('attendance_report')

    if selected_date:
        try:
            selected_date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()
            records = records.filter(date=selected_date_obj)
        except ValueError:
            messages.error(request, "Invalid date format.")
            return redirect('attendance_report')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance.csv"'
    writer = csv.writer(response)
    writer.writerow(['Date', 'Student Username', 'Course Name', 'Status'])

    for record in records:
        writer.writerow([
            record.date,
            record.student.user.username,
            record.course.name,
            record.status
        ])

    return response
