from rest_framework import serializers
from .models import Course, Lesson


class CourseSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "description",
            "is_active",
            "owner",
            "lessons_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner", "lessons_count", "created_at", "updated_at"]

    def get_lessons_count(self, obj):
        return obj.lessons.filter(deleted_at__isnull=True).count()

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            "id",
            "course",
            "title",
            "content",
            "order",
            "indentation",
            "is_published",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "course",
            "order",
            "indentation",
            "created_at",
            "updated_at",
        ]
