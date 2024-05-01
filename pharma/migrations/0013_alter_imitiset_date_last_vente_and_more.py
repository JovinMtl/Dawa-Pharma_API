# Generated by Django 5.0.4 on 2024-05-01 13:13

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pharma", "0012_imitiset_date_last_vente_imitiset_qte_entrant_big_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="imitiset",
            name="date_last_vente",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 5, 1, 13, 13, 48, 677977, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="umutientree",
            name="date_uzohererako",
            field=models.DateField(
                default=datetime.datetime(2024, 5, 1, 13, 13, 48, 676211)
            ),
        ),
        migrations.AlterField(
            model_name="umutientree",
            name="date_winjiriyeko",
            field=models.DateField(
                default=datetime.datetime(2024, 5, 1, 13, 13, 48, 676145)
            ),
        ),
        migrations.AlterField(
            model_name="umutisold",
            name="date_operation",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 5, 1, 13, 13, 48, 679419, tzinfo=datetime.timezone.utc
                )
            ),
        ),
    ]
