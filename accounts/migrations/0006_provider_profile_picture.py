# Generated by Django 5.1.1 on 2024-11-18 03:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0005_provider_city_provider_line1_provider_line2_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="provider",
            name="profile_picture",
            field=models.ImageField(
                blank=True, null=True, upload_to="profile_pictures/"
            ),
        ),
    ]
