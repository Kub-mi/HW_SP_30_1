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
    is_subscribed = serializers.SerializerMethodField()

    def get_lessons_count(self, obj):
        if hasattr(obj, "lesson_count"):
            return obj.lesson_count
        return obj.lessons.count()

    def get_is_subscribed(self, obj) -> bool:
        annotated = getattr(obj, "_is_subscribed", None)
        if annotated is not None:
            return bool(annotated)
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        return obj.subscriptions.filter(user_id=request.user.id).exists()

    class Meta:
        model = Course
        fields = ('id', 'title', 'preview', 'description', 'lessons_count', 'lessons', 'is_subscribed',)


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"
        validators = [
            OnlyYouTubeValidator(field="link"),
        ]
