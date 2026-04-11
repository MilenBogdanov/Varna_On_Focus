from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_user_email_verification_code_user_is_email_verified_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_banned',
            field=models.BooleanField(default=False, verbose_name='Деактивиране на профил (бан)'),
        ),
    ]