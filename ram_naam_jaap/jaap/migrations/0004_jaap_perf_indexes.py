import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jaap', '0003_cityjaapcount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jaapcount',
            name='date',
            field=models.DateField(db_index=True, default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='cityjaapcount',
            name='date',
            field=models.DateField(db_index=True, default=django.utils.timezone.now),
        ),
        migrations.AddIndex(
            model_name='jaapsession',
            index=models.Index(fields=['user', 'end_time'], name='jaap_session_user_end_idx'),
        ),
    ]
