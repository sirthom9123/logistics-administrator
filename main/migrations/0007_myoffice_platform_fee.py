# Generated by Django 4.1.6 on 2023-03-15 15:24

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0006_additionalinfo_paid"),
    ]

    operations = [
        migrations.AddField(
            model_name="myoffice",
            name="platform_fee",
            field=models.DecimalField(
                decimal_places=2,
                default=1.0,
                max_digits=7,
                validators=[django.core.validators.MinValueValidator(1)],
            ),
        ),
    ]
