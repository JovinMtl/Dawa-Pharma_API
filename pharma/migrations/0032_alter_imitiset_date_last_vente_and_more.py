# Generated by Django 5.0.4 on 2024-07-24 10:37

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pharma", "0031_alter_imitiset_date_last_vente_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="imitiset",
            name="date_last_vente",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 7, 24, 10, 37, 32, 510247, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="imitisuggest",
            name="previous_date",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 7, 24, 10, 37, 32, 514810, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="umutientree",
            name="date_uzohererako",
            field=models.DateField(
                default=datetime.datetime(2024, 7, 24, 10, 37, 32, 507112)
            ),
        ),
        migrations.AlterField(
            model_name="umutientree",
            name="date_winjiriyeko",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 7, 24, 10, 37, 32, 507045, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="umutientree",
            name="price_out_usd",
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name="umutientreebackup",
            name="date_uzohererako",
            field=models.DateField(
                default=datetime.datetime(2024, 7, 24, 10, 37, 32, 508609)
            ),
        ),
        migrations.AlterField(
            model_name="umutientreebackup",
            name="date_winjiriyeko",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 7, 24, 10, 37, 32, 508560, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="umutisold",
            name="date_operation",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 7, 24, 10, 37, 32, 512356, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="usdtobif",
            name="effect_date",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 7, 24, 10, 37, 32, 515905, tzinfo=datetime.timezone.utc
                )
            ),
        ),
    ]
