from . import views
from django.urls import path

urlpatterns = [
    path("", views.family_list, name="family-view"),
]
