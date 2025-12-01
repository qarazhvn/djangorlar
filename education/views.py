from django.shortcuts import get_object_or_404

from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from drf_spectacular.utils import extend_schema

from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ViewSet):
    """
    /api/v1/education/courses/
    """

    def get_queryset(self):
        qs = Course.objects.select_related("owner")
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            if is_active.lower() in ["true", "1"]:
                qs = qs.filter(is_active=True)
            elif is_active.lower() in ["false", "0"]:
                qs = qs.filter(is_active=False)
        return qs

    def list(self, request):
        serializer = CourseSerializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    @extend_schema(
        request=CourseSerializer,
        responses=CourseSerializer,
    )
    def create(self, request):
        serializer = CourseSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        course = get_object_or_404(self.get_queryset(), pk=pk)
        return Response(CourseSerializer(course).data)

    def update(self, request, pk=None):
        course = get_object_or_404(self.get_queryset(), pk=pk)

        if course.owner != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = CourseSerializer(
            course,
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        # владелец не меняется
        serializer.save(owner=course.owner)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        course = get_object_or_404(self.get_queryset(), pk=pk)
        if course.owner != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        course.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        course = get_object_or_404(self.get_queryset(), pk=pk)
        if course.owner != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if course.is_active:
            return Response(
                {"detail": "Course is already active."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        course.is_active = True
        course.save(update_fields=["is_active"])
        return Response(CourseSerializer(course).data)

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        course = get_object_or_404(self.get_queryset(), pk=pk)
        if course.owner != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if not course.is_active:
            return Response(
                {"detail": "Course is already inactive."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        course.is_active = False
        course.save(update_fields=["is_active"])
        return Response(CourseSerializer(course).data)

    @action(detail=True, methods=["get"])
    def lessons(self, request, pk=None):
        course = get_object_or_404(self.get_queryset(), pk=pk)
        lessons = course.lessons.filter(deleted_at__isnull=True).order_by("order")
        return Response(LessonSerializer(lessons, many=True).data)


class LessonViewSet(viewsets.ViewSet):
    """
    /api/v1/education/lessons/
    """

    def get_queryset(self):
        return Lesson.objects.select_related("course", "course__owner")

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "course_id": {"type": "integer", "example": 1},
                    "title": {"type": "string", "example": "Lesson 1"},
                    "content": {"type": "string", "example": "Lesson content"},
                },
                "required": ["course_id", "title"],
            }
        },
        responses=LessonSerializer,
    )
    def create(self, request):
        course_id = request.data.get("course_id")
        course = get_object_or_404(Course, id=course_id)

        if course.owner != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        order = Lesson.get_top_order_for_course(course)

        lesson = Lesson.objects.create(
            course=course,
            title=request.data.get("title"),
            content=request.data.get("content"),
            order=order,
            indentation=1,
        )

        return Response(LessonSerializer(lesson).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["put"])
    def move(self, request, pk=None):
        lesson = get_object_or_404(self.get_queryset(), pk=pk)
        course = lesson.course

        if course.owner != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        before_id = request.data.get("before_lesson_id")

        if before_id is None:
            new_order = Lesson.get_last_order_for_course(course)
            lesson.order = new_order
            lesson.indentation = 1
        else:
            before_lesson = get_object_or_404(
                self.get_queryset().filter(course=course), pk=before_id
            )

            prev = (
                Lesson.objects.filter(
                    course=course,
                    order__lt=before_lesson.order,
                )
                .order_by("-order")
                .first()
            )

            if prev:
                lesson.order = (prev.order + before_lesson.order) / 2
            else:
                lesson.order = before_lesson.order - 10

            lesson.indentation = min(before_lesson.indentation, 5)

        lesson.save(update_fields=["order", "indentation"])
        return Response(
            {
                "order": float(lesson.order),
                "indentation": lesson.indentation,
            }
        )

    def destroy(self, request, pk=None):
        lesson = get_object_or_404(self.get_queryset(), pk=pk)

        if lesson.course.owner != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        lesson.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        lesson = get_object_or_404(self.get_queryset(), pk=pk)

        if lesson.course.owner != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        lesson.is_published = True
        lesson.save(update_fields=["is_published"])
        return Response(LessonSerializer(lesson).data)

    @action(detail=True, methods=["post"])
    def unpublish(self, request, pk=None):
        lesson = get_object_or_404(self.get_queryset(), pk=pk)

        if lesson.course.owner != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        lesson.is_published = False
        lesson.save(update_fields=["is_published"])
        return Response(LessonSerializer(lesson).data)
