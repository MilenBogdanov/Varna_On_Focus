import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audit', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='newsaudit',
            name='performed_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='news_audit_entries',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Променено от',
            ),
        ),
        migrations.AddField(
            model_name='signalaudit',
            name='performed_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='signal_audit_entries',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Променено от',
            ),
        ),
    ]