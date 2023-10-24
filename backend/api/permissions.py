from rest_framework import permissions

NOT_ALLOWED_TO_CHANGE = 'У вас недостаточно прав.'


class ReadOnly(permissions.BasePermission):
    message = NOT_ALLOWED_TO_CHANGE

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS


class IsAdmin(permissions.BasePermission):
    message = NOT_ALLOWED_TO_CHANGE

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_staff
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated
            and request.user.is_staff
        )


class IsAuthor(permissions.BasePermission):
    message = NOT_ALLOWED_TO_CHANGE

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user == obj.author