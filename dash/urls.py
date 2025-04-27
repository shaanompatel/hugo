from django.urls import path, include
from . import views

app_name = 'dash'

urlpatterns = [
    path('', views.index, name='index'),
]