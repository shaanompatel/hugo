from django.shortcuts import render, get_object_or_404
from .models import Thread

def thread_list(request):
    threads = Thread.objects.order_by("-created_at")
    return render(request, "mail/threadlist.html", {"threads": threads})

def thread_detail(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    return render(request, "mail/threaddetail.html", {"thread": thread})