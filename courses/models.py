from django.db import models

class Course(models.Model):
    title = models.CharField(max_length=150, verbose_name='название')
    preview = models.FileField()
