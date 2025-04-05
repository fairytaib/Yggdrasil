from . import views
from django.urls import path

urlpatterns = [
    path("", views.get_owner, name="get_owner"),
    path(
        "add_family_member/",
        views.add_family_member, name="add_family_member"
        ),
]
