# Generated by Django 5.0.4 on 2025-01-16 10:22

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pharma", "0074_alter_assurance_last_paid_alter_assurance_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="assurance",
            name="last_paid",
            field=models.DateField(
                default=datetime.datetime(
                    1882, 2, 6, 10, 22, 17, 504069, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="bondecommand",
            name="date_paid",
            field=models.DateField(
                default=datetime.datetime(
                    1882, 2, 6, 10, 22, 17, 504069, tzinfo=datetime.timezone.utc
                )
            ),
        ),
    ]
