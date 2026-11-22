from django.shortcuts import render

from apps.dashboard.selectors import get_dashboard_data


def home(request):
    context = get_dashboard_data(user=request.user)
    return render(request, "pages/dashboard.html", context)
