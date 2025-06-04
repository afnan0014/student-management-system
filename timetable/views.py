from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import TimetableEntry, Holiday, Course
from .forms import TimetableForm, HolidayForm

# ------------------------------
# Admin: Add Timetable Entry
# ------------------------------
@staff_member_required
def add_timetable_entry(request):
    if request.method == 'POST':
        form = TimetableForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Timetable entry added successfully.")
            return redirect('add_timetable_entry')
    else:
        form = TimetableForm()

    return render(request, 'timetable/add_timetable.html', {'form': form})

# ------------------------------
# Staff: View Timetable with Day & Course Filters
# ------------------------------
@login_required
def staff_timetable_view(request):
    staff = request.user.staff_profile
    selected_day = request.GET.get('day', date.today().strftime('%A'))  # Default to today
    selected_course = request.GET.get('course', '')  # Default to empty (all courses)
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
    selected_day = request.GET.get('day', date.today().strftime('%A'))  # Default to today
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
