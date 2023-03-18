"""
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


"""
