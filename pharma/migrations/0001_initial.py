# Generated by Django 5.0.4 on 2024-04-26 08:39

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="UmutiEntree",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "date_winjiriyeko",
                    models.DateField(
                        default=datetime.datetime(2024, 4, 26, 8, 39, 38, 252349)
                    ),
                ),
                (
                    "date_uzohererako",
                    models.DateField(
                        default=datetime.datetime(2024, 4, 26, 8, 39, 38, 252422)
                    ),
                ),
                ("code_umuti", models.CharField(default="null", max_length=8)),
                ("name_umuti", models.CharField(default="null", max_length=30)),
                ("description_umuti", models.TextField()),
                ("type_umuti", models.CharField(default="null", max_length=10)),
                ("type_in", models.CharField(default="null", max_length=10)),
                ("type_out", models.CharField(default="null", max_length=10)),
                ("price_in", models.IntegerField(default=0)),
                ("price_out", models.IntegerField(default=0)),
                ("difference", models.IntegerField(default=0)),
                ("quantite_restant", models.IntegerField(default=0)),
                ("location", models.CharField(default="null", max_length=10)),
            ],
        ),
    ]
