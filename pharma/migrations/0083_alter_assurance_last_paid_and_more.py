# Generated by Django 5.0.4 on 2025-01-22 08:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pharma", "0082_imitiset_forme_alter_assurance_last_paid_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="assurance",
            name="last_paid",
            field=models.DateField(
                default=datetime.datetime(
                    1882, 2, 12, 8, 51, 18, 443162, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="bondecommand",
            name="date_paid",
            field=models.DateField(
                default=datetime.datetime(
                    1882, 2, 12, 8, 51, 18, 443162, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="bondecommand",
            name="date_prescri",
            field=models.DateField(
                default=datetime.datetime(
                    1882, 2, 12, 8, 51, 18, 443162, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="client",
            name="beneficiaire",
            field=models.CharField(default="inconnu", max_length=25),
        ),
        migrations.DeleteModel(
            name="BonDeCommande",
        ),
    ]
