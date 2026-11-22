from django.shortcuts import render

from apps.notifications.services import unread_notifications


def unread_list(request):
    return render(
        request,
        "pages/notification_list.html",
        {"notification_recipients": unread_notifications(user=request.user)},
    )
