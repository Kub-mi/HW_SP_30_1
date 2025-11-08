from rest_framework import serializers
from .models import Course, Lesson
from .validators import validate_youtube_url


class LessonShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ("id", "title", "description", "link")


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonShortSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ("id", "title", "preview", "description", "lessons_count", "lessons", "is_subscribed")

    def get_lessons_count(self, obj):
        return getattr(obj, "lesson_count", obj.lessons.count())

    def get_is_subscribed(self, obj):
        annotated = getattr(obj, "_is_subscribed", None)
        if annotated is not None:
            return bool(annotated)
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        return obj.subscriptions.filter(user_id=request.user.id).exists()


class LessonSerializer(serializers.ModelSerializer):
    link = serializers.URLField(
        required=False, allow_blank=True, allow_null=True,
        validators=[validate_youtube_url],
    )

    class Meta:
        model = Lesson
        fields = "__all__"


class SubscriptionToggleResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    course = serializers.IntegerField()
    is_subscribed = serializers.BooleanField()