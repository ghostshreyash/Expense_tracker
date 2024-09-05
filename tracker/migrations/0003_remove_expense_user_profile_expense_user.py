# tracker/migrations/0003_remove_expense_user_profile_expense_user.py
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tracker', '0002_remove_expense_user_userprofile_expense_user_profile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='expense',
            name='user_profile',
        ),
        migrations.AddField(
            model_name='expense',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
