from django.urls import path
from . import views

app_name = 'optimization'

urlpatterns = [
    path("", views.display_supply_chain_graph, name="optimization_main"),
]