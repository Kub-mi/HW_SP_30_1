from rest_framework.permissions import BasePermission


class IsModer(BasePermission):
    group_name = "moderators"
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               request.user.groups.filter(name=self.group_name).exists()
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)

class IsOwnerOrStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or getattr(obj, "owner", None) == request.user

class IsNotModer(BasePermission):
    group_name = "moderators"
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               not request.user.groups.filter(name=self.group_name).exists()

class IsModerOrOwnerOrStaff(BasePermission):
    """Разрешить доступ, если модератор ИЛИ владелец/staff."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    def has_object_permission(self, request, view, obj):
        is_moder = request.user.groups.filter(name="moderators").exists()
        return is_moder or request.user.is_staff or getattr(obj, "owner", None) == request.user
