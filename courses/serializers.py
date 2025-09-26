from rest_framework import serializers

from courses.models import Course, Lesson


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()

    def get_lessons_count(self, obj):
        if hasattr(obj, "lesson_count"):
            return obj.lesson_count
        return obj.lessons.count()

    class Meta:
        model = Course
        fields = ('id', 'title', 'preview', 'description', 'lessons_count')


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"



class LessonShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'
