from django.shortcuts import render


def ui_preview(request):
    return render(request, "pages/ui_preview.html")


def modal_preview(request):
    return render(request, "components/modal_preview.html")
