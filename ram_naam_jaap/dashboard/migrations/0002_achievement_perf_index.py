from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='achievement',
            index=models.Index(fields=['user', 'achievement_type'], name='dashboard_achv_user_type_idx'),
        ),
    ]
