from . import views
from django.urls import path

urlpatterns = [
    path("", views.get_owner, name="get_owner"),
    path(
        "add_family_member/",
        views.add_family_member, name="add_family_member"
        ),
    path(
        'family-view/<int:person_id>/',
        views.family_view,
        name='family_view'
        ),

]
