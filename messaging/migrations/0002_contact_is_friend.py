# Generated by Django 5.1.2 on 2024-11-21 03:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("messaging", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="contact",
            name="is_friend",
            field=models.BooleanField(default=False),
        ),
    ]
