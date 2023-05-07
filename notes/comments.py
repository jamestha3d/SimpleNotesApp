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

    
***********************
def delete(self, request: Request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


***********************

def perform_destroy(self, serializer):
        # get note id from request
        note_id = self.request.data.get('note_id')
        tag_name = self.request.data.get('name')
        note = Note.objects.get(pk=note_id)
        # use serializer to save note
        tag = Tag.objects.get(name=tag)
        note.tags.remove(tag)
        note.save()
        return super().perform_create(serializer)

    def get(self, request: Request, *args, **kwargs):

        return self.list(request, *args, **kwargs)


        
************************
class TagCreateView(generics.GenericAPIView, mixins.CreateModelMixin):
    
    #View for creating and listing Notes
    
    serializer_class = TagSerializer
    permission_classes = [IsAuthor]
    queryset = Tag.objects.all()

    def get_queryset(self, note_id):
        note = Note.objects.get(pk=note_id)
        return note.tags.all()

    # using mixin perform-hook to attach tag to current note
    def perform_create(self, serializer):
        # get note id from request
        user = self.request.user
        note_id = self.request.data.get('note_id')
        note = Note.objects.get(pk=note_id)

        if user == note.author:
            # use serializer to save note
            try:
                tag = serializer.save()
            except ValidationError:
                return Response("this tag don dey")
            note.tags.add(tag)
            note.save()
            return super().perform_create(serializer)
        else:
            return Response(data={"message": "You do not have permission to modify this note"})

    def post(self, request: Request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    ______________________
    path("tags/", views.TagCreateView.as_view(), name="tags")


    ______________________


    if tag_name is not None and tag_name is not "":
            try:
                tag = Tag.objects.get(name=tag_name)
            except ObjectDoesNotExist:
                tag = Tag.objects.create(name=tag_name)
            note.tags.add(tag)
            note.save()
            serializer = NoteSerializer(note, many=False)
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )
        else:
            return Response(data={"message": "Please provide tag name"})

class TagSerializer(serializers.ModelSerializer):
    # replace related string field with id

    class Meta:
        model = Tag
        fields = '__all__'

    def validate(self, attrs):
        invalid_tag = Tag.objects.filter(name=attrs['name']).exists()
        if invalid_tag:
            raise ValidationError("Invalid Tag")
        return super().validate(attrs)

    def create(self, validated_data):
        tag = super().create(validated_data)
        return tag
            
class NoteSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=50)
    # replace id in foreignKey-field with related name
    author = serializers.StringRelatedField(many=False)

    # tags = serializers.SlugRelatedField(many=True, read_only=True,
    #                                    slug_field='name')
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Note
        fields = '__all__'

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        note = Note.objects.create(**validated_data)
        for tag in tags_data:
            Tag.objects.create(note=note, **tags_data)
        return note

        ______________________
        def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        note = Note.objects.create(**validated_data)
        for tag in tags_data:
            Tag.objects.create(note=note, **tags_data)
        return note 






        def create(self, request):
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(data=serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

"""
