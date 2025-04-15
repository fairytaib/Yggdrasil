from . import views
from django.urls import path

urlpatterns = [
    path("", views.get_owner, name="get_owner"),
    path(
        "add_family_member/",
        views.add_family_member, name="add_family_member"
        ),
    path('add_self/', views.add_self, name='add_self'),
    path('pov/<int:pov_id>/delete/<int:person_id>/',
         views.delete_person, name='delete_person'),
    path('pov/<int:pov_id>/edit/<int:person_id>/',
         views.edit_person, name='edit_person'),
    path(
        'family_view/<int:person_id>/',
        views.view_family,
        name='family_view'
        ),
    path("view_details/<int:person_id>/",
         views.view_details, name="view_details"),
]
