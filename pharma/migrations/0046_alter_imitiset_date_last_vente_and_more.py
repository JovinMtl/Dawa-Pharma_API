# Generated by Django 5.0.4 on 2024-12-14 09:01

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pharma", "0045_alter_imitiset_date_last_vente_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="imitiset",
            name="date_last_vente",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 12, 14, 9, 1, 54, 208574, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="imitisuggest",
            name="previous_date",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 12, 14, 9, 1, 54, 210763, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="umutientree",
            name="date_uzohererako",
            field=models.DateField(
                default=datetime.datetime(2024, 12, 14, 9, 1, 54, 207468)
            ),
        ),
        migrations.AlterField(
            model_name="umutientree",
            name="date_winjiriyeko",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 12, 14, 9, 1, 54, 207447, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="umutientreebackup",
            name="date_uzohererako",
            field=models.DateField(
                default=datetime.datetime(2024, 12, 14, 9, 1, 54, 207957)
            ),
        ),
        migrations.AlterField(
            model_name="umutientreebackup",
            name="date_winjiriyeko",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 12, 14, 9, 1, 54, 207940, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="umutisold",
            name="date_operation",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 12, 14, 9, 1, 54, 210148, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="usdtobif",
            name="effect_date",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 12, 14, 9, 1, 54, 211064, tzinfo=datetime.timezone.utc
                )
            ),
        ),
    ]
