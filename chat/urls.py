from django.urls import path, include
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/', views.chat, name='process_message'),
]