# Generated by Django 5.0.4 on 2024-12-23 15:42

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pharma", "0053_rename_code_umuti_imitiset_code_med_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="imitiset",
            name="date_last_vente",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 12, 23, 15, 42, 28, 103248, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="imitisuggest",
            name="previous_date",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 12, 23, 15, 42, 28, 107689, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="umutientree",
            name="date_entrant",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 12, 23, 15, 42, 28, 99650, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="umutientree",
            name="date_peremption",
            field=models.DateField(
                default=datetime.datetime(2024, 12, 23, 15, 42, 28, 99721)
            ),
        ),
        migrations.AlterField(
            model_name="umutientreebackup",
            name="date_entrant",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 12, 23, 15, 42, 28, 101385, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="umutientreebackup",
            name="date_peremption",
            field=models.DateField(
                default=datetime.datetime(2024, 12, 23, 15, 42, 28, 101430)
            ),
        ),
        migrations.AlterField(
            model_name="umutisold",
            name="date_operation",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 12, 23, 15, 42, 28, 105912, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="usdtobif",
            name="effect_date",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 12, 23, 15, 42, 28, 108381, tzinfo=datetime.timezone.utc
                )
            ),
        ),
    ]
