from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsOrganizer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['organizer', 'admin']


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['staff', 'admin']


class IsAttendee(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'attendee'