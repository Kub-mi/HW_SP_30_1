from rest_framework import serializers

from courses.models import Course, Lesson
from .validators import OnlyYouTubeValidator


class LessonShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ("id", "title", "description", "link")


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonShortSerializer(many=True, read_only=True)

    def get_lessons_count(self, obj):
        if hasattr(obj, "lesson_count"):
            return obj.lesson_count
        return obj.lessons.count()

    class Meta:
        model = Course
        fields = ('id', 'title', 'preview', 'description', 'lessons_count', 'lessons')


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"
        validators = [
            OnlyYouTubeValidator(field="video_url"),
            # Можно добавить и для materials, если materials — одиночная ссылка:
            # OnlyYouTubeValidator(field="materials"),
        ]
