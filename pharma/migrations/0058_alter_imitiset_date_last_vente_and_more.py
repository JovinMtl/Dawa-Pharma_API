# Generated by Django 5.0.4 on 2024-12-24 13:03

import datetime
import django.db.models.deletion
import pharma.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pharma", "0057_alter_bondecommande_organization_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="imitiset",
            name="date_last_vente",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 12, 24, 13, 3, 17, 399947, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="imitisuggest",
            name="previous_date",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 12, 24, 13, 3, 17, 401468, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="umutientree",
            name="date_entrant",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 12, 24, 13, 3, 17, 398798, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="umutientree",
            name="date_peremption",
            field=models.DateField(
                default=datetime.datetime(2024, 12, 24, 13, 3, 17, 398819)
            ),
        ),
        migrations.AlterField(
            model_name="umutientreebackup",
            name="date_entrant",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 12, 24, 13, 3, 17, 399303, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="umutientreebackup",
            name="date_peremption",
            field=models.DateField(
                default=datetime.datetime(2024, 12, 24, 13, 3, 17, 399319)
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
                    2024, 12, 24, 13, 3, 17, 400868, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="usdtobif",
            name="effect_date",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 12, 24, 13, 3, 17, 401761, tzinfo=datetime.timezone.utc
                )
            ),
        ),
    ]
