# timetable/views.py
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import TimetableEntry, Holiday, Course
from .forms import TimetableForm
from collections import defaultdict
from courses.models import Subject
from accounts.models import StaffProfile
from notifications.utils import notify_users  # Import the notification utility

@staff_member_required
def add_timetable_entry(request):
    if request.method == 'POST':
        form = TimetableForm(request.POST)
        if form.is_valid():
            timetable_entry = form.save(commit=False)
            timetable_entry.created_by = request.user
            timetable_entry.save()

            # Send notification to staff and students
            notify_users('timetable_added', request.user, course=timetable_entry.course, timetable=timetable_entry)

            if 'add_another' in request.POST:
                messages.success(request, "✅ Entry added. You can add another one.")
                return redirect('add_timetable_entry')
            elif 'save_only' in request.POST:
                messages.success(request, "✅ Timetable entry added successfully.")
                return redirect('timetable_list')
        else:
            messages.error(request, "❌ Please correct the errors below.")
    else:
        form = TimetableForm()

    return render(request, 'timetable/add_timetable.html', {'form': form})

@login_required
def staff_timetable_view(request):
    staff = request.user.staff_profile
    selected_day = request.GET.get('day', date.today().strftime('%A'))
    selected_course = request.GET.get('course', '')
    holiday = Holiday.objects.filter(date=date.today()).first()

    day_choices = [
        ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday')
    ]

    course_choices = Course.objects.all()
    entries = TimetableEntry.objects.filter(staff=staff, day=selected_day).order_by('period_number')

    if selected_course:
        entries = entries.filter(course__name=selected_course)

    return render(request, 'timetable/staff_timetable.html', {
        'timetable': entries,
        'holiday': holiday,
        'today': date.today(),
        'day_choices': day_choices,
        'selected_day': selected_day,
        'course_choices': course_choices,
        'selected_course': selected_course
    })

@login_required
def student_timetable_view(request):
    student = request.user.student_profile
    selected_day = request.GET.get('day', date.today().strftime('%A'))
    holiday = Holiday.objects.filter(date=date.today()).first()

    day_choices = [
        ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday')
    ]

    entries = TimetableEntry.objects.filter(
        course=student.course,
        semester=student.course.semester,
        day=selected_day
    ).order_by('period_number')

    return render(request, 'timetable/student_timetable.html', {
        'timetable': entries,
        'holiday': holiday,
        'today': date.today(),
        'day_choices': day_choices,
        'selected_day': selected_day
    })

@staff_member_required
def timetable_list_view(request):
    from .models import TimetableEntry, Holiday
    from accounts.models import StaffProfile

    course = request.GET.get('course')
    staff = request.GET.get('staff')
    day = request.GET.get('day')

    entries = TimetableEntry.objects.select_related('course', 'subject', 'staff__user').all()
    if course:
        entries = entries.filter(course_id=course)
    if staff:
        entries = entries.filter(staff_id=staff)
    if day:
        entries = entries.filter(day=day)

    context = {
        'entries': entries.order_by('day', 'period_number'),
        'courses': Course.objects.all(),
        'staffs': StaffProfile.objects.select_related('user'),
        'days': [day for day, _ in TimetableEntry.DAY_CHOICES],
        'selected': {'course': course, 'staff': staff, 'day': day},
    }
    return render(request, 'timetable/timetable_list.html', context)

@staff_member_required
def edit_timetable_entry(request, pk):
    entry = get_object_or_404(TimetableEntry, pk=pk)
    form = TimetableForm(request.POST or None, instance=entry)
    if form.is_valid():
        form.save()
        messages.success(request, "Updated successfully!")
        return redirect('timetable_list')
    return render(request, 'timetable/add_timetable.html', {'form': form})

@staff_member_required
def delete_timetable_entries(request):
    if request.method == 'POST':
        ids = request.POST.get('entry_ids', '').split(',')
        TimetableEntry.objects.filter(id__in=ids).delete()
        messages.success(request, "Selected entries deleted.")
    return redirect('timetable_list')