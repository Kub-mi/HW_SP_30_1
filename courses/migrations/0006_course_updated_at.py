import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0005_subscription'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, default=django.utils.timezone.now, verbose_name='обновлено'),
            preserve_default=False,
        ),
    ]
