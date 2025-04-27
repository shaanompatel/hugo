from django.urls import path
from . import views

app_name = 'mail'


urlpatterns = [
    path("threads/", views.thread_list, name="thread_list"),
    path("threads/<int:thread_id>/", views.thread_detail, name="thread_detail"),
]
