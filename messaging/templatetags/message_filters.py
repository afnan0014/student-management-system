from django import template

register = template.Library()

@register.filter
def filter_read(recipients):
    return recipients.filter(is_read=True)

@register.filter
def filter_unread(recipients):
    return recipients.filter(is_read=False)

@register.filter
def filter_nested_replies(replies, parent_reply):
    return replies.filter(parent_message=parent_reply)