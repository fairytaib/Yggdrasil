from . import views
from django.urls import path

urlpatterns = [
    path("", views.get_owner, name="get_owner"),
    path(
        "add_family_member/",
        views.add_family_member, name="add_family_member"
        ),
    path('add-self/', views.add_self, name='add_self'),
    path('delete/<int:person_id>/', views.delete_person, name='delete_person'),
    path('edit/<int:person_id>/', views.edit_person, name='edit_person'),
    path(
        'family-view/<int:person_id>/',
        views.family_view,
        name='family_view'
        ),
]
