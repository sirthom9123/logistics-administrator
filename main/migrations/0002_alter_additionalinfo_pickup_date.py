# Generated by Django 4.1.6 on 2023-02-06 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="additionalinfo",
            name="pickup_date",
            field=models.DateTimeField(help_text="Date & Time", null=True),
        ),
    ]
