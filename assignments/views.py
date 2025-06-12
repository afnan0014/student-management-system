from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Assignment, Submission, AssignmentFile, AssignmentImage, AssignmentLink, SubmissionFile, SubmissionImage
from courses.models import Course, Subject
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Q
import logging
from notifications.utils import notify_users

# Set up logging to debug user role issues
logger = logging.getLogger(__name__)

@login_required
def assignment_list(request):
    user = request.user
    logger.debug(f"User: {user.username}, is_staff: {user.is_staff}, groups: {[group.name for group in user.groups.all()]}")

    # Check if user is in the Staff group (as an alternative to is_staff)
    is_staff_user = user.is_staff or user.groups.filter(name='Staff').exists()
    
    if is_staff_user:
        logger.debug(f"User {user.username} recognized as staff, rendering staff assignment list.")
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
        logger.debug(f"User {user.username} recognized as student, rendering student assignment list.")
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
        logger.debug(f"User {user.username} not authorized for assignments, redirecting based on role.")
        messages.error(request, "You are not authorized to access assignments.")
        if user.groups.filter(name='Admin').exists():
            return redirect('admin_dashboard')
        elif user.groups.filter(name='Staff').exists():
            return redirect('staff_dashboard')
        elif user.groups.filter(name='Student').exists():
            return redirect('student_dashboard')
        else:
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

        link_contents = request.POST.getlist('link_content')
        links = []
        for link in link_contents:
            if link:
                link_obj = AssignmentLink.objects.create(url=link)
                links.append(link_obj)

        files = []
        for file in request.FILES.getlist('file_content'):
            file_obj = AssignmentFile.objects.create(file=file)
            files.append(file_obj)

        images = []
        for image in request.FILES.getlist('image_content'):
            image_obj = AssignmentImage.objects.create(image=image)
            images.append(image_obj)

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
            text_content=text_content if text_content else None,
        )

        if links:
            assignment.links.set(links)
        if files:
            assignment.files.set(files)
        if images:
            assignment.images.set(images)

        if assignment_type == 'individual':
            students = User.objects.filter(
                groups__name='Student',
                student_profile__course=course,
                student_profile__semester=semester
            )
            if not students.exists():
                messages.warning(request, f"No students found for {course.name} in semester {semester}.")
            for student in students:
                assignment.students.add(student)
        else:
            num_students = int(request.POST.get('num_students', 0))
            student_ids = request.POST.getlist('students')
            
            if num_students > 0 and student_ids:
                for student_id in student_ids:
                    student = get_object_or_404(User, id=student_id)
                    if not student.student_profile.course == course:
                        messages.error(request, f"Student {student.username} does not belong to the selected course.")
                        return render(request, 'assignments/create_assignment.html', {'courses': courses})
                    assignment.students.add(student)
            else:
                messages.error(request, "Please select at least one student for group work.")
                return render(request, 'assignments/create_assignment.html', {'courses': courses})

        # Send notification to students
        notify_users('assignment_added', request.user, course=course, assignment=assignment)

        messages.success(request, "Assignment created successfully!")
        return redirect('assignment_list')

    return render(request, 'assignments/create_assignment.html', {
        'courses': courses,
    })

@login_required
def edit_assignment(request, assignment_id):
    if not (request.user.is_staff or request.user.groups.filter(name='Staff').exists()):
        messages.error(request, "Only staff can edit assignments.")
        return redirect('assignment_list')

    assignment = get_object_or_404(Assignment, id=assignment_id, assigned_by=request.user)
    courses = Course.objects.filter(assigned_staff=request.user)

    students = User.objects.filter(
        groups__name='Student',
        student_profile__course=assignment.course,
        student_profile__semester=assignment.semester
    )

    if request.method == 'POST':
        assignment.title = request.POST.get('title')
        assignment.description = request.POST.get('description')
        course_id = request.POST.get('course')
        subject_id = request.POST.get('subject')
        course = get_object_or_404(Course, id=course_id, assigned_staff=request.user)
        subject = get_object_or_404(Subject, id=subject_id, course=course)
        assignment.course = course
        assignment.subject = subject
        assignment.semester = course.semester
        assignment.deadline = request.POST.get('deadline')
        assignment.text_content = request.POST.get('text_content', '') or None

        link_contents = request.POST.getlist('link_content')
        new_links = []
        for link in link_contents:
            if link:
                link_obj = AssignmentLink.objects.create(url=link)
                new_links.append(link_obj)
        assignment.links.set(new_links)

        new_files = []
        for file in request.FILES.getlist('file_content'):
            file_obj = AssignmentFile.objects.create(file=file)
            new_files.append(file_obj)
        if new_files:
            assignment.files.set(new_files)

        new_images = []
        for image in request.FILES.getlist('image_content'):
            image_obj = AssignmentImage.objects.create(image=image)
            new_images.append(image_obj)
        if new_images:
            assignment.images.set(new_images)

        assignment.save()

        student_ids = request.POST.getlist('students')
        assignment.students.clear()
        for student_id in student_ids:
            student = get_object_or_404(User, id=student_id)
            if not student.student_profile.course == course:
                messages.error(request, f"Student {student.username} does not belong to the selected course.")
                return render(request, 'assignments/edit_assignment.html', {
                    'assignment': assignment,
                    'courses': courses,
                    'students': students,
                })
            assignment.students.add(student)

        messages.success(request, "Assignment updated successfully!")
        return redirect('assignment_list')

    return render(request, 'assignments/edit_assignment.html', {
        'assignment': assignment,
        'courses': courses,
        'students': students,
    })

@login_required
def delete_assignment(request, assignment_id):
    if not (request.user.is_staff or request.user.groups.filter(name='Staff').exists()):
        messages.error(request, "Only staff can delete assignments.")
        return redirect('assignment_list')

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
        files = []
        for file in request.FILES.getlist('file_submission'):
            file_obj = SubmissionFile.objects.create(file=file)
            files.append(file_obj)

        images = []
        for image in request.FILES.getlist('image_submission'):
            image_obj = SubmissionImage.objects.create(image=image)
            images.append(image_obj)

        current_time = timezone.now()
        if assignment.assignment_type == 'group':
            group_students = assignment.students.all()
            existing_submissions = Submission.objects.filter(assignment=assignment).count()
            submission, created = Submission.objects.get_or_create(
                assignment=assignment,
                student=request.user,
                defaults={
                    'text_submission': text_submission if text_submission else None,
                    'submitted_at': current_time,
                    'status': 'pending',
                }
            )
            if not created:
                submission.text_submission = text_submission if text_submission else None
                submission.submitted_at = current_time
                submission.save()

            if files:
                submission.files.set(files)
            if images:
                submission.images.set(images)

            if existing_submissions + 1 == group_students.count():
                status = 'on_time' if current_time <= assignment.deadline else 'late'
                Submission.objects.filter(assignment=assignment).update(status=status)
        else:
            submission, created = Submission.objects.get_or_create(
                assignment=assignment,
                student=request.user,
                defaults={
                    'text_submission': text_submission if text_submission else None,
                    'submitted_at': current_time,
                    'status': 'on_time' if current_time <= assignment.deadline else 'late',
                }
            )
            if not created:
                submission.text_submission = text_submission if text_submission else None
                submission.submitted_at = current_time
                submission.status = 'on_time' if current_time <= assignment.deadline else 'late'
                submission.save()

            if files:
                submission.files.set(files)
            if images:
                submission.images.set(images)

        # Send notification to staff
        notify_users('assignment_submitted', request.user, course=assignment.course, submission=submission)

        messages.success(request, "Assignment submitted successfully!")
        return redirect('assignment_list')

    return render(request, 'assignments/submit_assignment.html', {'assignment': assignment})

@login_required
def view_submissions(request, assignment_id):
    if not (request.user.is_staff or request.user.groups.filter(name='Staff').exists()):
        messages.error(request, "Only staff can view submissions.")
        return redirect('assignment_list')

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
    logger.debug(f"Fetching students for course_id: {course_id}")
    
    if not course_id:
        logger.warning("Missing course_id in request.")
        return JsonResponse({'students': []}, status=400)
    
    try:
        course = get_object_or_404(Course, id=course_id, assigned_staff=request.user)
        semester = course.semester
        students = User.objects.filter(
            groups__name='Student',
            student_profile__course__id=course_id,
            student_profile__semester=semester
        ).select_related('student_profile')
        
        logger.debug(f"Found {students.count()} students for course_id: {course_id}, semester: {semester}")
        
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
    logger.debug(f"Fetching subjects for course_id: {course_id}")
    
    if not course_id:
        logger.warning("Missing course_id in request.")
        return JsonResponse({'subjects': []}, status=400)
    
    try:
        course = get_object_or_404(Course, id=course_id, assigned_staff=request.user)
        subjects = Subject.objects.filter(course=course)
        subject_list = [{'id': subject.id, 'name': subject.name} for subject in subjects]
        return JsonResponse({'subjects': subject_list, 'semester': course.semester})
    except Exception as e:
        logger.error(f"Error fetching subjects: {str(e)}")
        return JsonResponse({'subjects': []}, status=500)