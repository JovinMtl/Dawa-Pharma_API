# Generated by Django 5.0.4 on 2024-05-10 19:04

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pharma", "0016_umutireportsell_alter_imitiset_date_last_vente_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="umutisold",
            name="price_in",
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name="umutisold",
            name="price_total",
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name="imitiset",
            name="date_last_vente",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 5, 10, 19, 4, 12, 187101, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="umutientree",
            name="date_uzohererako",
            field=models.DateField(
                default=datetime.datetime(2024, 5, 10, 19, 4, 12, 185230)
            ),
        ),
        migrations.AlterField(
            model_name="umutientree",
            name="date_winjiriyeko",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 5, 10, 19, 4, 12, 185143, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="umutisold",
            name="date_operation",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 5, 10, 19, 4, 12, 188143, tzinfo=datetime.timezone.utc
                )
            ),
        ),
    ]
