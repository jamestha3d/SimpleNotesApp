from . import views
from django.urls import path

urlpatterns = [
    path("homepage/", views.homepage, name="notes_home"),
    path("", views.NoteListCreateView.as_view(), name="list_notes"),
    path("<int:pk>/", views.NoteRetrieveUpdateDeleteView.as_view(), name="note_detail"),
    path("current_user/", views.get_notes_for_current_user, name="current_user"),
    path("all_notes/", views.ListNotesForAdmin.as_view(),
         name="all_notes"),
    path("filter/<tag>", views.ListNotesByTagFilter.as_view(),
         name="filter_tag"),
    path("search/<keyword>", views.ListSearchNotesByKeyWord.as_view(),
         name="search_keyword"),
    path("add_tag/<int:pk>/", views.add_tag_to_note, name="add_tag"),
    path("remove_tag/<int:pk>/", views.remove_tag_from_note, name="remove_tag"),
    path("tags/<note_id>", views.TagCreateDeleteView.as_view(), name="tags")
]
