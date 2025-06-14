from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.models import User
import logging

from .models import Assignment, Submission, AssignmentFile, AssignmentImage, AssignmentLink, SubmissionFile, SubmissionImage
from courses.models import Course, Subject
from notifications.utils import notify_users

logger = logging.getLogger(__name__)

@login_required
def assignment_list(request):
    user = request.user
    is_staff_user = user.is_staff or user.groups.filter(name='Staff').exists()

    if is_staff_user:
        assignments = Assignment.objects.filter(assigned_by=user).order_by('-created_at')
        search_query = request.GET.get('search', '')
        if search_query:
            assignments = assignments.filter(
                Q(title__icontains=search_query) |
                Q(course__name__icontains=search_query)
            )

        for assignment in assignments:
            assignment.has_pending = Submission.objects.filter(assignment=assignment, status='pending').exists()
            assignment.has_late = Submission.objects.filter(assignment=assignment, status='late').exists()
            assignment.has_on_time = Submission.objects.filter(assignment=assignment, status='on_time').exists()

        if request.method == 'POST' and 'bulk_delete' in request.POST:
            assignment_ids = request.POST.getlist('assignment_ids')
            Assignment.objects.filter(id__in=assignment_ids, assigned_by=user).delete()
            messages.success(request, "Selected assignments deleted successfully!")
            return redirect('assignment_list')

        return render(request, 'assignments/staff_assignment_list.html', {'assignments': assignments, 'search_query': search_query})

    elif user.groups.filter(name='Student').exists():
        assignments = Assignment.objects.filter(students=user).order_by('-created_at')
        search_query = request.GET.get('search', '')
        if search_query:
            try:
                from datetime import datetime
                search_date = datetime.strptime(search_query, '%Y-%m-%d')
                assignments = assignments.filter(
                    Q(title__icontains=search_query) |
                    Q(course__name__icontains=search_query) |
                    Q(deadline__date=search_date.date())
                )
            except ValueError:
                assignments = assignments.filter(
                    Q(title__icontains=search_query) |
                    Q(course__name__icontains=search_query)
                )

        submissions = Submission.objects.filter(student=user)
        submitted_assignment_ids = submissions.values_list('assignment_id', flat=True)
        return render(request, 'assignments/student_assignment_list.html', {
            'assignments': assignments,
            'submitted_assignment_ids': submitted_assignment_ids,
            'search_query': search_query,
        })

    else:
        messages.error(request, "You are not authorized to access assignments.")
        return redirect('login')


@login_required
def create_assignment(request):
    if not (request.user.is_staff or request.user.groups.filter(name='Staff').exists()):
        messages.error(request, "Only staff can create assignments.")
        return redirect('assignment_list')

    courses = Course.objects.filter(assigned_staff=request.user)
    if not courses.exists():
        messages.error(request, "You are not assigned to any courses. Please contact the admin.")
        return redirect('assignment_list')

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        course_id = request.POST.get('course')
        subject_id = request.POST.get('subject')
        assignment_type = request.POST.get('assignment_type', 'individual')
        deadline = request.POST.get('deadline')
        text_content = request.POST.get('text_content', '')

        links = [AssignmentLink.objects.create(url=link) for link in request.POST.getlist('link_content') if link]
        files = [AssignmentFile.objects.create(file=file) for file in request.FILES.getlist('file_content')]
        images = [AssignmentImage.objects.create(image=image) for image in request.FILES.getlist('image_content')]

        course = get_object_or_404(Course, id=course_id, assigned_staff=request.user)
        subject = get_object_or_404(Subject, id=subject_id, course=course)
        semester = course.semester

        assignment = Assignment.objects.create(
            title=title,
            description=description,
            course=course,
            subject=subject,
            semester=semester,
            assigned_by=request.user,
            assignment_type=assignment_type,
            deadline=deadline,
            text_content=text_content or None,
        )

        if links: assignment.links.set(links)
        if files: assignment.files.set(files)
        if images: assignment.images.set(images)

        if assignment_type == 'individual':
            students = User.objects.filter(groups__name='Student', student_profile__course=course, student_profile__semester=semester)
            for student in students:
                assignment.students.add(student)
        else:
            student_ids = request.POST.getlist('students')
            if student_ids:
                for student_id in student_ids:
                    student = get_object_or_404(User, id=student_id)
                    assignment.students.add(student)
            else:
                messages.error(request, "Please select at least one student for group work.")
                return render(request, 'assignments/create_assignment.html', {'courses': courses})

        notify_users('assignment_added', request.user, course=course, assignment=assignment)
        messages.success(request, "Assignment created successfully!")
        return redirect('assignment_list')

    return render(request, 'assignments/create_assignment.html', {'courses': courses})


@login_required
def edit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id, assigned_by=request.user)
    courses = Course.objects.filter(assigned_staff=request.user)
    students = User.objects.filter(groups__name='Student', student_profile__course=assignment.course, student_profile__semester=assignment.semester)

    if request.method == 'POST':
        assignment.title = request.POST.get('title')
        assignment.description = request.POST.get('description')
        course = get_object_or_404(Course, id=request.POST.get('course'), assigned_staff=request.user)
        subject = get_object_or_404(Subject, id=request.POST.get('subject'), course=course)
        assignment.course = course
        assignment.subject = subject
        assignment.semester = course.semester
        assignment.deadline = request.POST.get('deadline')
        assignment.text_content = request.POST.get('text_content', '') or None

        links = [AssignmentLink.objects.create(url=link) for link in request.POST.getlist('link_content') if link]
        files = [AssignmentFile.objects.create(file=file) for file in request.FILES.getlist('file_content')]
        images = [AssignmentImage.objects.create(image=image) for image in request.FILES.getlist('image_content')]

        if links: assignment.links.set(links)
        if files: assignment.files.set(files)
        if images: assignment.images.set(images)

        assignment.students.clear()
        for student_id in request.POST.getlist('students'):
            student = get_object_or_404(User, id=student_id)
            assignment.students.add(student)

        assignment.save()
        messages.success(request, "Assignment updated successfully!")
        return redirect('assignment_list')

    return render(request, 'assignments/edit_assignment.html', {
        'assignment': assignment,
        'courses': courses,
        'students': students,
    })


@login_required
def delete_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id, assigned_by=request.user)
    assignment.delete()
    messages.success(request, "Assignment deleted successfully!")
    return redirect('assignment_list')


@login_required
def view_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if request.user not in assignment.students.all() and not (request.user.is_staff or request.user.groups.filter(name='Staff').exists()):
        messages.error(request, "You are not authorized to view this assignment.")
        return redirect('assignment_list')

    submission = Submission.objects.filter(assignment=assignment, student=request.user).first()
    return render(request, 'assignments/view_assignment.html', {
        'assignment': assignment,
        'submission': submission,
    })


@login_required
def submit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if request.user not in assignment.students.all():
        messages.error(request, "You are not authorized to submit this assignment.")
        return redirect('assignment_list')

    if request.method == 'POST':
        text_submission = request.POST.get('text_submission', '')
        files = [SubmissionFile.objects.create(file=file) for file in request.FILES.getlist('file_submission')]
        images = [SubmissionImage.objects.create(image=image) for image in request.FILES.getlist('image_submission')]

        current_time = timezone.now()

        if assignment.assignment_type == 'group':
            submission, created = Submission.objects.get_or_create(
                assignment=assignment,
                student=request.user,
                defaults={
                    'text_submission': text_submission or None,
                    'submitted_at': current_time,
                    'status': 'pending',
                }
            )
            if not created:
                submission.text_submission = text_submission or None
                submission.submitted_at = current_time
                submission.save()

            if files: submission.files.set(files)
            if images: submission.images.set(images)

            if Submission.objects.filter(assignment=assignment).count() == assignment.students.count():
                status = 'on_time' if current_time <= assignment.deadline else 'late'
                Submission.objects.filter(assignment=assignment).update(status=status)

        else:
            submission, created = Submission.objects.get_or_create(
                assignment=assignment,
                student=request.user,
                defaults={
                    'text_submission': text_submission or None,
                    'submitted_at': current_time,
                    'status': 'on_time' if current_time <= assignment.deadline else 'late',
                }
            )
            if not created:
                submission.text_submission = text_submission or None
                submission.submitted_at = current_time
                submission.status = 'on_time' if current_time <= assignment.deadline else 'late'
                submission.save()

            if files: submission.files.set(files)
            if images: submission.images.set(images)

        notify_users('assignment_submitted', request.user, course=assignment.course, submission=submission)
        messages.success(request, "Assignment submitted successfully!")
        return redirect('assignment_list')

    return render(request, 'assignments/submit_assignment.html', {'assignment': assignment})


@login_required
def view_submissions(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id, assigned_by=request.user)
    submissions = Submission.objects.filter(assignment=assignment)

    assigned_students = assignment.students.all()
    submitted_students = User.objects.filter(submissions__assignment=assignment)
    non_submitted_students = assigned_students.exclude(id__in=submitted_students)

    return render(request, 'assignments/view_submissions.html', {
        'assignment': assignment,
        'submissions': submissions,
        'submitted_students': submitted_students,
        'non_submitted_students': non_submitted_students,
    })


def get_students_by_course(request):
    course_id = request.GET.get('course_id')
    if not course_id:
        return JsonResponse({'students': []}, status=400)

    try:
        course = get_object_or_404(Course, id=course_id, assigned_staff=request.user)
        semester = course.semester
        students = User.objects.filter(
            groups__name='Student',
            student_profile__course__id=course_id,
            student_profile__semester=semester
        ).select_related('student_profile')

        student_list = [
            {
                'id': student.id,
                'username': student.username,
                'full_name': student.get_full_name() or student.username,
                'batch_number': student.student_profile.batch_number if student.student_profile else None
            }
            for student in students
        ]
        return JsonResponse({'students': student_list})
    except Exception as e:
        logger.error(f"Error fetching students: {str(e)}")
        return JsonResponse({'students': []}, status=500)


def get_subjects_by_course(request):
    course_id = request.GET.get('course_id')
    if not course_id:
        return JsonResponse({'subjects': []}, status=400)

    try:
        course = get_object_or_404(Course, id=course_id, assigned_staff=request.user)
        subjects = Subject.objects.filter(course=course)
        subject_list = [{'id': subject.id, 'name': subject.name} for subject in subjects]
        return JsonResponse({'subjects': subject_list, 'semester': course.semester})
    except Exception as e:
        logger.error(f"Error fetching subjects: {str(e)}")
        return JsonResponse({'subjects': []}, status=500)
