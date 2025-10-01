from rest_framework import viewsets, generics, permissions
from django.db.models import Count, Prefetch

from courses.models import Course, Lesson
from courses.permissions import IsModer, IsOwnerOrStaff, IsNotModer, IsModerOrOwnerOrStaff
from courses.serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().order_by('id')
    serializer_class = CourseSerializer

    def get_permissions(self):
        # Базовое требование: JWT
        if self.action in ("list", "retrieve"):
            # смотреть: модерам любой объект; немодерам — фильтруем в get_queryset
            perms = [permissions.IsAuthenticated]
        elif self.action in ("update", "partial_update"):
            # редактировать: модератор ИЛИ владелец/staff
            perms = [permissions.IsAuthenticated, IsModerOrOwnerOrStaff]
        elif self.action == "create":
            # модераторам создавать нельзя
            perms = [permissions.IsAuthenticated, IsNotModer]
        elif self.action == "destroy":
            # модераторам удалять нельзя; только владелец/staff
            perms = [permissions.IsAuthenticated, IsOwnerOrStaff]
        else:
            perms = [permissions.IsAuthenticated]
        return [p() if isinstance(p, type) else p for p in perms]

    def get_queryset(self):
        qs = (
            Course.objects
            .annotate(lesson_count=Count("lessons", distinct=True))
            .prefetch_related(
                Prefetch(
                    "lessons",
                    queryset=Lesson.objects.only("id", "title", "description", "link", "course_id").order_by("id")
                )
            )
        )
        user = self.request.user
        # Немодератор видит только свои курсы
        if user.is_authenticated and not user.groups.filter(name="moderators").exists() and not user.is_staff:
            return qs.filter(owner=user)
        return qs

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonCreateAPIView(generics.CreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, IsNotModer]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListAPIView(generics.ListAPIView):
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Lesson.objects.all()
        user = self.request.user
        # Немодератор видит только свои уроки
        if user.is_authenticated and not user.groups.filter(name="moderators").exists() and not user.is_staff:
            return qs.filter(owner=user)
        return qs


class LessonRetrieveApiView(generics.RetrieveAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsModerOrOwnerOrStaff]


class LessonUpdateAPIView(generics.UpdateAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsModerOrOwnerOrStaff]


class LessonDestroyAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]
