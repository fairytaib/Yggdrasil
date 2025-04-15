
from django.urls import path
from . import views

urlpatterns = [
    path('', views.person_of_the_day_view, name='person_of_the_day'),
]
