from rest_framework import viewsets, generics
from django.db.models import Count, Prefetch

from courses.models import Course, Lesson
from courses.serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer

    def get_queryset(self):
        return (
            Course.objects
            .annotate(lesson_count=Count("lessons", distinct=True))
            .prefetch_related(
                Prefetch(
                    "lessons",
                    queryset=Lesson.objects.only("id", "title", "description", "link", "course_id")
                    .order_by("id")  # или по нужному полю
                )
            )
        )


class LessonCreateAPIView(generics.CreateAPIView):
    serializer_class = LessonSerializer


class LessonListAPIView(generics.ListAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()


class LessonRetrieveApiView(generics.RetrieveAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()


class LessonUpdateAPIView(generics.UpdateAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()


class LessonDestroyAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
