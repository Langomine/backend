# Generated by Django 5.1.1 on 2024-10-05 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_voice_language'),
    ]

    operations = [
        migrations.AddField(
            model_name='voice',
            name='words',
            field=models.JSONField(null=True),
        ),
    ]
