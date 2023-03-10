# Generated by Django 4.1.6 on 2023-03-10 22:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0004_rename_lat_measurement_d_lat_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="additionalinfo",
            name="email",
            field=models.EmailField(max_length=254, null=True),
        ),
        migrations.AddField(
            model_name="additionalinfo",
            name="phone_number",
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name="additionalinfo",
            name="pickup_date",
            field=models.DateTimeField(null=True),
        ),
    ]
