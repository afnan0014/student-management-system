from django.urls import reverse
from .models import Notification
from django.contrib.auth.models import User
from courses.models import Course

def send_notification(recipient, message, redirect_url=None):
    Notification.objects.create(
        recipient=recipient,
        message=message,
        redirect_url=redirect_url
    )

def notify_users(action, user, course=None, **kwargs):
    """
    Notify users based on the action with role-specific messages and redirects.
    """
    if action == 'exam_added':
        exam = kwargs.get('exam')
        course = exam.course
        staff = User.objects.filter(groups__name='Staff', staff_profile__course=course)
        students = User.objects.filter(groups__name='Student', student_profile__course=course)
        admins = User.objects.filter(is_superuser=True)
        message = f"{exam.name} exam added"
        redirect_url_admin = reverse('exam_list')
        redirect_url_staff = reverse('staff_dashboard')
        redirect_url_student = reverse('student_dashboard')

        for admin in admins:
            send_notification(admin, message, redirect_url_admin)
        for staff_member in staff:
            send_notification(staff_member, message, redirect_url_staff)
        for student in students:
            send_notification(student, message, redirect_url_student)

    elif action == 'timetable_added':
        timetable = kwargs.get('timetable')
        course = timetable.course
        staff = User.objects.filter(groups__name='Staff', staff_profile__course=course)
        students = User.objects.filter(groups__name='Student', student_profile__course=course)
        admins = User.objects.filter(is_superuser=True)
        message = f"Timetable update for {course.name}"
        redirect_url_admin = reverse('timetable_list')
        redirect_url_staff = reverse('staff_timetable')
        redirect_url_student = reverse('student_timetable')

        for admin in admins:
            send_notification(admin, message, redirect_url_admin)
        for staff_member in staff:
            send_notification(staff_member, message, redirect_url_staff)
        for student in students:
            send_notification(student, message, redirect_url_student)

    elif action == 'message_sent':
        message_obj = kwargs.get('message')
        sender = user.username
        recipients = kwargs.get('recipients', set())
        message = f"1 message from {sender}"
        redirect_url = reverse('messaging:inbox') + "?view=received"

        if user.is_superuser:
            for recipient in recipients:
                if recipient != user:
                    send_notification(recipient, message, redirect_url)
        elif user.groups.filter(name='Staff').exists():
            for recipient in recipients:
                if recipient != user and (recipient.groups.filter(name='Student').exists() or recipient.is_superuser):
                    send_notification(recipient, message, redirect_url)
        elif user.groups.filter(name='Student').exists():
            for recipient in recipients:
                if recipient != user and (recipient.groups.filter(name='Staff').exists() or recipient.is_superuser):
                    send_notification(recipient, message, redirect_url)

    elif action == 'assignment_added':
        assignment = kwargs.get('assignment')
        course = assignment.course
        students = assignment.students.all()
        message = f"New assignment: {assignment.title} in {course.name}"
        redirect_url = reverse('assignment_list')

        for student in students:
            send_notification(student, message, redirect_url)

    elif action == 'assignment_submitted':
        submission = kwargs.get('submission')
        assignment = submission.assignment
        staff = assignment.assigned_by
        message = f"{submission.student.username} submitted {assignment.title}"
        redirect_url = reverse('view_submissions', args=[assignment.id])

        send_notification(staff, message, redirect_url)

    elif action == 'marks_added':
        mark = kwargs.get('mark')
        student = mark.student.user
        message = f"Marks for {mark.exam.name}: {mark.marks_obtained}"
        redirect_url = reverse('report_card')

        send_notification(student, message, redirect_url)

    elif action == 'attendance_marked':
        attendance = kwargs.get('attendance')
        student = attendance.student.user
        message = f"Attendance on {attendance.date}: {attendance.status}"
        redirect_url = reverse('student_attendance_view')

        send_notification(student, message, redirect_url)