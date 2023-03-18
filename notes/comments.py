"""

**********************
in app views.py
#custom view set
class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer


in project urls.py
# from notes.views import NoteViewSet
# from rest_framework.routers import DefaultRouter

# router = DefaultRouter()

# router.register("", NoteViewSet, basename="notes")

*************************
GET REQUEST OBJECTS
item is gotten as data from request.

#modify the queryset
def get_queryset(self):
    user = self.request.user
    return Note.objects.filter(author=user)

************************
Get URL PARAMETERS
in urls.py
...
path("notes_for/<username>", views.ListNotesForAuthor.as_view(),
         name="notes_for_current_user")
...

in views.py
def get_queryset(self):
    username = self.kwargs.get("username")
    return Note.objects.filter(author__username = username)

author__username is username field lookup on Myobject model.

***********************

GET QUERY PARAMS

urls.py
path("notes_for/", views.ListNotesForAuthor.as_view(),
         name="notes_for_current_user")

views.py

def get_queryset(self):
        queryset = Note.objects.all()
        username = self.request.query_params.get("username") or None
        if username is not None:
            return Note.objects.filter(author__username=username)
        return queryset


author__username is username field lookup on Myobject model.

    
"""
