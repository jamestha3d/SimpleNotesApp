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
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_auto_schema
from rest_framework.validators import ValidationError
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view, action, permission_classes

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
        note = serializer.save(author=user)
        tags = self.request.data.get('tags')
        if tags:
            for tag in tags:
                if note.tag_not_exists(tag):
                    Tag.objects.create(note=note, name=tag)

        return super().perform_create(serializer)

    @swagger_auto_schema(
        operation_summary="List user notes",
        operation_description="This returns all notes for the current user"
    )
    def get(self, request: Request, *args, **kwargs):

        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create note",
        operation_description="Create a note"
    )
    def post(self, request: Request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class NoteRetrieveUpdateDeleteView(generics.GenericAPIView, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    serializer_class = NoteSerializer
    queryset = Note.objects.all()
    permission_classes = [AuthorOrPublic]

    @swagger_auto_schema(
        operation_summary="Retrieves a note by id",
        operation_description="This retrieves a note by an id"
    )
    def get(self, request: Request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update note by id",
        operation_description="This updates a note by an id"
    )
    def put(self, request: Request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete note by id",
        operation_description="This deletes a note by an id"
    )
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

    @swagger_auto_schema(
        operation_summary="List all notes for admin",
        operation_description="This lists all public and private notes. Must have admin privilege"
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ListNotesByTagFilter(generics.GenericAPIView, mixins.ListModelMixin):
    """Filter note by tag"""
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [IsAuthor]

    # we can accept the tags as part of the request.
    def get_queryset(self):
        user = self.request.user
        notes = user.notes.all()
        tag = self.kwargs.get("tag")
        return user.notes.filter(tags__name=tag)

    @swagger_auto_schema(
        operation_summary="Filter note by tag name",
        operation_description="This filters notes by a given tag for current user "
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ListSearchNotesByKeyWord(generics.GenericAPIView, mixins.ListModelMixin):
    """Search note by keyword"""
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [IsAuthor]

    def get_queryset(self):
        keyword = self.kwargs.get("keyword")
        user = self.request.user
        return user.notes.filter(body__icontains=keyword)

    @swagger_auto_schema(
        operation_summary="Search note by keyword",
        operation_description="This returns notes that contain a given keyword for current user "
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class TagCreateDeleteView(generics.GenericAPIView, mixins.CreateModelMixin, mixins.DestroyModelMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]

    # using mixin perform-hook to attach note to current user
    def perform_create(self, serializer):
        user = self.request.user
        note = Note.objects.get(pk=self.kwargs.get('note_id'))
        if note:
            if note.author == user:

                serializer.save(note=note)
                return super().perform_create(serializer)
            else:
                return Response(data={"error": "you do not have"})

    def post(self, request: Request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


@api_view(http_method_names=['POST'])
@permission_classes([IsAuthenticated])
def add_tag_to_note(request: Request, pk):
    note = Note.objects.get(pk=pk)
    user = request.user
    tag_name = request.data.get('tag')

    if user == note.author:
        # check if tag exists in note
        if note.tag_not_exists(tag_name):
            tag = Tag.objects.create(note=note, name=tag_name)
            serializer = NoteSerializer(note)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data={"message": "Tag already exists"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(data={"message": "You do not have permission to modify this note"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(http_method_names=['DELETE'])
@permission_classes([IsAuthenticated])
def remove_tag_from_note(request: Request, pk):
    note = Note.objects.get(pk=pk)
    user = request.user
    tag_name = request.data.get('tag')
    if note.author == user:
        tag = Tag.objects.filter(name=tag_name)
        if tag:
            tag[0].delete()
            serializer = NoteSerializer(note)
            return Response({
                "message": f"tag {tag_name} deleted successfully",
                "data": serializer.data
            },
                status=status.HTTP_200_OK
            )
        else:
            return Response(data={"message": "Cannot delete non-existent tag"})
    else:
        return Response(data={"message": "You do not have permission to delete this tag"}, status=status.HTTP_401_UNAUTHORIZED)


# alternative implementation using modelviewset
class NoteViewSet(ModelViewSet):
    serializer_class = NoteSerializer
    permission_classes = []
    queryset = Note.objects.all()

    def get_queryset(self):
        queryset = Note.objects.all()
        username = self.request.query_params.get("username") or None
        if username is not None:
            return Note.objects.filter(author__username=username)
        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        note = serializer.save(author=user)
        tags = self.request.data.get('tags')
        if tags:
            for tag in tags:
                if note.tag_not_exists(tag):
                    Tag.objects.create(note=note, name=tag)

        return super().perform_create(serializer)

    @action(
        detail=True,
        methods=['GET', 'POST'],
        permission_classes=(AllowAny,),
        url_path=r'taglist/(?P<title_id>[^/.]+)'
        )
    def tags(self, request, pk=None, title_id=None):
        note = Note.objects.get(pk=pk)
        tags = note.tags.all()
        print("got here")
        return Response(data=TagSerializer(tags, many=True).data)