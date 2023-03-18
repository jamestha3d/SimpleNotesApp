from . import views
from django.urls import path

urlpatterns = [
    path("homepage/", views.homepage, name="notes_home"),
    path("", views.NoteListCreateView.as_view(), name="list_notes"),
    path("<int:pk>/", views.NoteRetrieveUpdateDeleteView.as_view(), name="note_detail"),
    path("current_user/", views.get_notes_for_current_user, name="current_user")
]
