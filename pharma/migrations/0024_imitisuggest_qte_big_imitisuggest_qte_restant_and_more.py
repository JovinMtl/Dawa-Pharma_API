# Generated by Django 5.0.4 on 2024-06-28 18:54

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pharma", "0023_imitisuggest_previous_date_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="imitisuggest",
            name="qte_big",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="imitisuggest",
            name="qte_restant",
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="imitiset",
            name="date_last_vente",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 6, 28, 18, 54, 38, 198519, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="imitisuggest",
            name="previous_date",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 6, 28, 18, 54, 38, 201325, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="umutientree",
            name="date_uzohererako",
            field=models.DateField(
                default=datetime.datetime(2024, 6, 28, 18, 54, 38, 196704)
            ),
        ),
        migrations.AlterField(
            model_name="umutientree",
            name="date_winjiriyeko",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 6, 28, 18, 54, 38, 196622, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="umutisold",
            name="date_operation",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 6, 28, 18, 54, 38, 199610, tzinfo=datetime.timezone.utc
                )
            ),
        ),
    ]
