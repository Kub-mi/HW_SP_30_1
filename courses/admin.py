from django.contrib import admin
from .models import Course, Lesson

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("id", "title")
    search_fields = ("title",)  # важно для autocomplete_fields

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "course")
    search_fields = ("title",)  # важно для autocomplete_fields
    autocomplete_fields = ("course",)  # опционально, чтобы в уроке искать курс