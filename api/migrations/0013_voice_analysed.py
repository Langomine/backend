# Generated by Django 5.1.1 on 2024-11-03 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0012_question"),
    ]

    operations = [
        migrations.AddField(
            model_name="voice",
            name="analysed",
            field=models.JSONField(null=True),
        ),
    ]