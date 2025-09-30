from rest_framework import viewsets, generics, permissions
from django.db.models import Count, Prefetch

from courses.models import Course, Lesson
from courses.permissions import IsModer, IsOwnerOrStaff, IsNotModer, IsModerOrOwnerOrStaff
from courses.serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().order_by('id')
    serializer_class = CourseSerializer

    def get_permissions(self):
        # Базово требуем JWT
        if self.action in ("list", "retrieve"):
            perms = [permissions.IsAuthenticated]
        elif self.action in ("update", "partial_update"):
            perms = [permissions.IsAuthenticated, IsModerOrOwnerOrStaff]
        elif self.action == "create":
            perms = [permissions.IsAuthenticated, IsNotModer]          # модераторам нельзя
        elif self.action == "destroy":
            perms = [permissions.IsAuthenticated, IsNotModer, IsOwnerOrStaff]  # модераторам нельзя, только owner/staff
        else:
            perms = [permissions.IsAuthenticated]
        return [p() if isinstance(p, type) else p for p in perms]

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
    permission_classes = [permissions.IsAuthenticated, IsNotModer]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListAPIView(generics.ListAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class LessonRetrieveApiView(generics.RetrieveAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class LessonUpdateAPIView(generics.UpdateAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsModerOrOwnerOrStaff]


class LessonDestroyAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsNotModer, IsOwnerOrStaff]
