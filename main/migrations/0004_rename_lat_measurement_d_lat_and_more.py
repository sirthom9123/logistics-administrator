# Generated by Django 4.1.6 on 2023-03-08 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0003_measurement_lat_measurement_lng"),
    ]

    operations = [
        migrations.RenameField(
            model_name="measurement", old_name="lat", new_name="d_lat",
        ),
        migrations.RenameField(
            model_name="measurement", old_name="lng", new_name="d_lng",
        ),
        migrations.AddField(
            model_name="measurement",
            name="l_lat",
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="measurement",
            name="l_lng",
            field=models.CharField(max_length=100, null=True),
        ),
    ]
