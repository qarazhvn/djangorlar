from rest_framework.permissions import BasePermission
from .models import Course, Lesson


class IsCourseOwner(BasePermission):
    def has_object_permission(self, request, view, obj: Course):
        return obj.owner == request.user


class IsLessonOwner(BasePermission):
    def has_object_permission(self, request, view, obj: Lesson):
        return obj.course.owner == request.user
