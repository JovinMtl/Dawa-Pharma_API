# Generated by Django 5.0.4 on 2024-12-14 12:06

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pharma", "0054_alter_imitiset_date_last_vente_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="bondecommande",
            name="montant_caisse",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="bondecommande",
            name="montant_dette",
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="imitiset",
            name="date_last_vente",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 12, 14, 12, 6, 59, 14105, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="imitisuggest",
            name="previous_date",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 12, 14, 12, 6, 59, 18747, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="umutientree",
            name="date_uzohererako",
            field=models.DateField(
                default=datetime.datetime(2024, 12, 14, 12, 6, 59, 11318)
            ),
        ),
        migrations.AlterField(
            model_name="umutientree",
            name="date_winjiriyeko",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 12, 14, 12, 6, 59, 11262, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="umutientreebackup",
            name="date_uzohererako",
            field=models.DateField(
                default=datetime.datetime(2024, 12, 14, 12, 6, 59, 12656)
            ),
        ),
        migrations.AlterField(
            model_name="umutientreebackup",
            name="date_winjiriyeko",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 12, 14, 12, 6, 59, 12605, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="umutisold",
            name="bon_de_commande",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="pharma.bondecommande",
            ),
        ),
        migrations.AlterField(
            model_name="umutisold",
            name="date_operation",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 12, 14, 12, 6, 59, 17062, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="usdtobif",
            name="effect_date",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 12, 14, 12, 6, 59, 19594, tzinfo=datetime.timezone.utc
                )
            ),
        ),
    ]
