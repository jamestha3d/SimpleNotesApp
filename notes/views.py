from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework import status, generics, mixins
from rest_framework.decorators import api_view, APIView, permission_classes
from .models import Note, Tag
from .serializers import NoteSerializer, TagSerializer
from django.shortcuts import get_object_or_404
from accounts.serializers import CurrentUserNotesSerializer
from .permissions import ReadOnly, AuthorOrReadOnly, IsAuthor, AuthorOrPublic

# from rest_framework import viewsets


@api_view(http_method_names=["GET", "POST"])
@permission_classes([AllowAny])
def homepage(request: Request):
    if request.method == "POST":
        data = request.data
        response = {"message": "Hello world", "data": data}
        return Response(data=response, status=status.HTTP_201_CREATED)
    response = {"message": "Hello World"}
    return Response(data=response, status=status.HTTP_200_OK)


class NoteListCreateView(generics.GenericAPIView, mixins.ListModelMixin, mixins.CreateModelMixin):
    """
        View for creating and listing Notes
    """
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]
    queryset = Note.objects.all()

    # modify the default queryset
    def get_queryset(self):
        user = self.request.user
        return Note.objects.filter(author=user)

    # using mixin perform-hook to attach note to current user
    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(author=user)
        return super().perform_create(serializer)

    def get(self, request: Request, *args, **kwargs):

        return self.list(request, *args, **kwargs)

    def post(self, request: Request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class NoteRetrieveUpdateDeleteView(generics.GenericAPIView, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    serializer_class = NoteSerializer
    queryset = Note.objects.all()
    permission_classes = [AuthorOrPublic]

    def get(self, request: Request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request: Request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request: Request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


@api_view(http_method_names=['GET'])
@permission_classes([IsAuthenticated])
def get_notes_for_current_user(request: Request):
    user = request.user
    serializer = CurrentUserNotesSerializer(
        instance=user, context={"request": request})
    return Response(
        data=serializer.data,
        status=status.HTTP_200_OK
    )


class ListNotesForAdmin(generics.GenericAPIView, mixins.ListModelMixin):
    """Admin can see all notes"""
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ListNotesByTagFilter(generics.GenericAPIView, mixins.ListModelMixin):
    """Filter note by tag"""
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    # we can accept the tags as part of the request.
    def get_queryset(self):
        user = self.request.user
        notes = user.notes.all()
        # tag = self.request.data.get('tag') or None
        tag = self.kwargs.get("tag")
        return user.notes.filter(tags__name=tag)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ListSearchNotesByKeyWord(generics.GenericAPIView, mixins.ListModelMixin):
    """Search note by keyword"""
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        keyword = self.kwargs.get("keyword")
        user = self.request.user
        return user.notes.filter(body__icontains=keyword)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
