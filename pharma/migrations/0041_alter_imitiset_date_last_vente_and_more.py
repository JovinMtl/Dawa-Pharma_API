# Generated by Django 5.0.4 on 2024-12-13 14:21

import datetime
import django.db.models.deletion
import pharma.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pharma", "0040_umutisold_bon_de_commande_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="imitiset",
            name="date_last_vente",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 12, 13, 14, 21, 57, 317094, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="imitisuggest",
            name="previous_date",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 12, 13, 14, 21, 57, 318646, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="umutientree",
            name="date_uzohererako",
            field=models.DateField(
                default=datetime.datetime(2024, 12, 13, 14, 21, 57, 315723)
            ),
        ),
        migrations.AlterField(
            model_name="umutientree",
            name="date_winjiriyeko",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 12, 13, 14, 21, 57, 315680, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="umutientreebackup",
            name="date_uzohererako",
            field=models.DateField(
                default=datetime.datetime(2024, 12, 13, 14, 21, 57, 316419)
            ),
        ),
        migrations.AlterField(
            model_name="umutientreebackup",
            name="date_winjiriyeko",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 12, 13, 14, 21, 57, 316402, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="umutisold",
            name="bon_de_commande",
            field=models.ForeignKey(
                default=pharma.models.getBonDeCommandeInstance,
                on_delete=django.db.models.deletion.CASCADE,
                to="pharma.bondecommande",
            ),
        ),
        migrations.AlterField(
            model_name="umutisold",
            name="date_operation",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 12, 13, 14, 21, 57, 318012, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="usdtobif",
            name="effect_date",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 12, 13, 14, 21, 57, 318970, tzinfo=datetime.timezone.utc
                )
            ),
        ),
    ]
