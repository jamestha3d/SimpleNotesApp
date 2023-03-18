from rest_framework.permissions import BasePermission, SAFE_METHODS


class ReadOnly(BasePermission):
    # overwrite the default has_permission
    def has_permission(self, request, view):
        # returns true for get and false for post
        return request.method in SAFE_METHODS


class AuthorOrReadOnly(BasePermission):
    # check if current user has object permission
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return request.user == obj.author


class IsAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.author


class AuthorOrPublic(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            if obj.public:
                return True
        return request.user == obj.author
