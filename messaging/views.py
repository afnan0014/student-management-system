from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q, Count
from django.urls import reverse
from django.http import Http404
from .models import Message, MessageRecipient, MessageAttachment
from .forms import MessageForm
from django.contrib.auth.models import User
from courses.models import Course
from accounts.models import StaffProfile, StudentProfile
from datetime import timedelta

@login_required
def inbox(request):
    view_type = request.GET.get('view', 'sent')
    filter_type = request.GET.get('filter', '')

    received_messages = MessageRecipient.objects.filter(recipient=request.user).order_by('-message__timestamp')
    sent_messages = Message.objects.filter(sender=request.user).order_by('-timestamp').annotate(
        read_count=Count('recipients', filter=Q(recipients__is_read=True)),
        total_recipients=Count('recipients')
    )

    if request.user.groups.filter(name='Staff').exists():
        if view_type == 'received':
            if filter_type == 'admin':
                received_messages = received_messages.filter(message__sender__is_superuser=True)
            elif filter_type == 'students':
                received_messages = received_messages.filter(message__sender__groups__name='Student')
        else:
            if filter_type == 'admin':
                sent_messages = sent_messages.filter(recipients__recipient__is_superuser=True)
            elif filter_type == 'students':
                sent_messages = sent_messages.filter(recipients__recipient__groups__name='Student')
    elif request.user.groups.filter(name='Student').exists():
        if view_type == 'received':
            if filter_type == 'admin':
                received_messages = received_messages.filter(message__sender__is_superuser=True)
            elif filter_type == 'staff':
                received_messages = received_messages.filter(message__sender__groups__name='Staff')
        else:
            if filter_type == 'admin':
                sent_messages = sent_messages.filter(recipients__recipient__is_superuser=True)
            elif filter_type == 'staff':
                sent_messages = sent_messages.filter(recipients__recipient__groups__name='Staff')

    context = {
        'received_messages': received_messages,
        'sent_messages': sent_messages,
        'view': view_type,
        'filter_type': filter_type,
    }
    return render(request, 'messaging/inbox.html', context)

@login_required
def admin_messages(request, message_type, view_type='sent'):
    view_type = request.GET.get('view', view_type)

    sent_messages = Message.objects.filter(sender=request.user, message_type=message_type, is_announcement=True).order_by('-timestamp').annotate(
        read_count=Count('recipients', filter=Q(recipients__is_read=True)),
        total_recipients=Count('recipients')
    )
    received_messages = MessageRecipient.objects.filter(recipient=request.user, message__is_announcement=True).order_by('-message__timestamp')

    return render(request, 'messaging/admin_messages.html', {
        'sent_messages': sent_messages,
        'received_messages': received_messages,
        'message_type': message_type,
        'view': view_type,
    })

@login_required
def send_message(request):
    if request.method == 'POST':
        form = MessageForm(request.POST, user=request.user)
        if form.is_valid():
            message = form.save(commit=False, sender=request.user)
            message.is_announcement = request.user.is_superuser
            message.save()

            links = request.POST.getlist('links[]')
            files = request.FILES.getlist('files[]')

            for link in links:
                if link.strip():
                    MessageAttachment.objects.create(
                        message=message,
                        attachment_type='link',
                        link=link.strip()
                    )

            for file in files:
                if file:
                    MessageAttachment.objects.create(
                        message=message,
                        attachment_type='file',
                        file=file
                    )

            recipients = set()
            if request.user.is_superuser:
                message_type = form.cleaned_data['message_type']
                if message_type == 'all':
                    staff = User.objects.filter(groups__name='Staff')
                    students = User.objects.filter(groups__name='Student')
                    recipients.update(staff)
                    recipients.update(students)
                elif message_type == 'staff_only':
                    recipients.update(User.objects.filter(groups__name='Staff'))
                elif message_type == 'students_only':
                    course = form.cleaned_data['course']
                    semester = form.cleaned_data['semester']
                    if not (course and semester):
                        messages.error(request, "Please select both course and semester for students-only messages.")
                        message.delete()
                        return redirect('messaging:send_message')
                    student_profiles = StudentProfile.objects.filter(course=course, semester=semester)
                    recipients.update(User.objects.filter(student_profile__in=student_profiles))
            elif request.user.groups.filter(name='Staff').exists():
                message_type = form.cleaned_data['staff_message_type']
                if message_type == 'personal':
                    recipient = form.cleaned_data['recipient']
                    if recipient:
                        try:
                            staff_profile = StaffProfile.objects.get(user=request.user)
                            recipient_profile = StudentProfile.objects.get(user=recipient)
                            if staff_profile.course != recipient_profile.course:
                                messages.error(request, "You can only message students in your assigned course.")
                                message.delete()
                                return redirect('messaging:send_message')
                            recipients.add(recipient)
                        except (StaffProfile.DoesNotExist, StudentProfile.DoesNotExist):
                            messages.error(request, "Invalid user profile.")
                            message.delete()
                            return redirect('messaging:send_message')
                    else:
                        messages.error(request, "Please select a recipient.")
                        message.delete()
                        return redirect('messaging:send_message')
                elif message_type == 'group':
                    try:
                        staff_profile = StaffProfile.objects.get(user=request.user)
                        course = form.cleaned_data['course']
                        semester = form.cleaned_data['semester']
                        if not (course and semester):
                            messages.error(request, "Please select both course and semester for group messages.")
                            message.delete()
                            return redirect('messaging:send_message')
                        if staff_profile.course != course:
                            messages.error(request, "You can only message students in your assigned course.")
                            message.delete()
                            return redirect('messaging:send_message')
                        student_profiles = StudentProfile.objects.filter(course=course, semester=semester)
                        recipients.update(User.objects.filter(student_profile__in=student_profiles))
                    except StaffProfile.DoesNotExist:
                        messages.error(request, "Staff profile not found.")
                        message.delete()
                        return redirect('messaging:send_message')
            else:  # Student
                try:
                    student_profile = StudentProfile.objects.get(user=request.user)
                    course = student_profile.course
                    semester = student_profile.semester
                    staff_profiles = StaffProfile.objects.filter(course=course)
                    recipients.update(User.objects.filter(staff_profile__in=staff_profiles))
                except StudentProfile.DoesNotExist:
                    messages.error(request, "Student profile not found.")
                    message.delete()
                    return redirect('messaging:send_message')

            if not recipients:
                messages.error(request, "No valid recipients found.")
                message.delete()
                return redirect('messaging:send_message')

            for recipient in recipients:
                if recipient != request.user:
                    MessageRecipient.objects.create(message=message, recipient=recipient)

            messages.success(request, "Message sent successfully!")
            view_type = request.GET.get('view', 'sent')
            if request.user.is_superuser:
                url = reverse('messaging:admin_messages', kwargs={'message_type': message.message_type})
                return redirect(f"{url}?view={view_type}")
            else:
                url = reverse('messaging:inbox')
                return redirect(f"{url}?view={view_type}")
    else:
        form = MessageForm(user=request.user)
    return render(request, 'messaging/send_message.html', {
        'form': form,
    })

@login_required
def message_detail(request, message_id):
    try:
        message = Message.objects.get(id=message_id)
    except Message.DoesNotExist:
        messages.error(request, "The message does not exist.")
        return redirect('messaging:inbox')

    if message.sender == request.user:
        msg_recipient = None
    else:
        try:
            msg_recipient = MessageRecipient.objects.get(message_id=message_id, recipient=request.user)
            if not msg_recipient.is_read:
                msg_recipient.is_read = True
                msg_recipient.read_timestamp = timezone.now()
                msg_recipient.save()
        except MessageRecipient.DoesNotExist:
            messages.error(request, "You do not have access to this message.")
            return redirect('messaging:inbox')

    replies = Message.objects.filter(parent_message=message).order_by('timestamp')
    recipients = MessageRecipient.objects.filter(message=message)

    # Handle reply submission
    if request.method == 'POST':
        content = request.POST.get('content')
        parent_reply_id = request.POST.get('parent_reply_id')  # For replies to replies
        if content:
            new_reply = Message(
                sender=request.user,
                content=content,
                parent_message=message if not parent_reply_id else Message.objects.get(id=parent_reply_id),
                timestamp=timezone.now(),
                message_type='all' if request.user.is_superuser else 'personal'
            )
            new_reply.save()

            # Add recipients (same as the original message)
            for recipient in recipients:
                if recipient.recipient != request.user:
                    MessageRecipient.objects.create(
                        message=new_reply,
                        recipient=recipient.recipient
                    )

            messages.success(request, "Reply sent successfully!")
            return redirect('messaging:message_detail', message_id=message_id)

    return render(request, 'messaging/message_detail.html', {
        'msg_recipient': msg_recipient,
        'message': message,
        'replies': replies,
    })

@login_required
def edit_message(request, message_id):
    message = get_object_or_404(Message, id=message_id, sender=request.user)
    time_diff = timezone.now() - message.timestamp
    if not request.user.is_superuser and time_diff > timedelta(minutes=3):
        messages.error(request, "You can only edit messages within 3 minutes of sending them. This message can no longer be edited.")
        view_type = request.GET.get('view', 'sent')
        if request.user.is_superuser:
            message_type = message.message_type if message.is_announcement else 'all'
            url = reverse('messaging:admin_messages', kwargs={'message_type': message_type})
            return redirect(f"{url}?view={view_type}")
        else:
            url = reverse('messaging:inbox')
            return redirect(f"{url}?view={view_type}")

    if request.method == 'POST':
        form = MessageForm(request.POST, instance=message, user=request.user)
        if form.is_valid():
            message = form.save(commit=False)
            message.last_edited = timezone.now()
            message.save()

            message.attachments.all().delete()

            links = request.POST.getlist('links[]')
            files = request.FILES.getlist('files[]')

            for link in links:
                if link.strip():
                    MessageAttachment.objects.create(
                        message=message,
                        attachment_type='link',
                        link=link.strip()
                    )

            for file in files:
                if file:
                    MessageAttachment.objects.create(
                        message=message,
                        attachment_type='file',
                        file=file
                    )

            messages.success(request, "Message updated successfully!")
            view_type = request.GET.get('view', 'sent')
            if request.user.is_superuser:
                message_type = message.message_type if message.is_announcement else 'all'
                url = reverse('messaging:admin_messages', kwargs={'message_type': message_type})
                return redirect(f"{url}?view={view_type}")
            else:
                url = reverse('messaging:inbox')
                return redirect(f"{url}?view={view_type}")
    else:
        form = MessageForm(instance=message, user=request.user)
        has_link_attachments = message.attachments.filter(attachment_type='link').exists()
        has_file_attachments = message.attachments.filter(attachment_type='file').exists()
    return render(request, 'messaging/edit_message.html', {
        'form': form,
        'message': message,
        'has_link_attachments': has_link_attachments,
        'has_file_attachments': has_file_attachments,
    })

@login_required
def delete_message(request, message_id):
    try:
        message = get_object_or_404(Message, id=message_id, sender=request.user)
        message.delete()
        messages.success(request, "Message deleted successfully!")
    except Http404:
        messages.error(request, "The message does not exist or you do not have permission to delete it.")

    view_type = request.GET.get('view', 'sent')
    if request.user.is_superuser:
        message_type = message.message_type if 'message' in locals() and message else 'all'
        url = reverse('messaging:admin_messages', kwargs={'message_type': message_type})
        return redirect(f"{url}?view={view_type}")
    else:
        url = reverse('messaging:inbox')
        return redirect(f"{url}?view={view_type}")