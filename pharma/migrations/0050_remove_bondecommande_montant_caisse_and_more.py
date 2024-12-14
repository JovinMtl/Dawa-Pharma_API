# Generated by Django 5.0.4 on 2024-12-14 09:16

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pharma", "0049_alter_bondecommande_montant_caisse_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="bondecommande",
            name="montant_caisse",
        ),
        migrations.RemoveField(
            model_name="bondecommande",
            name="montant_dette",
        ),
        migrations.AlterField(
            model_name="bondecommande",
            name="organization",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="pharma.assurance",
            ),
        ),
        migrations.AlterField(
            model_name="imitiset",
            name="date_last_vente",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 12, 14, 9, 16, 35, 835343, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="imitisuggest",
            name="previous_date",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 12, 14, 9, 16, 35, 839848, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="umutientree",
            name="date_uzohererako",
            field=models.DateField(
                default=datetime.datetime(2024, 12, 14, 9, 16, 35, 832615)
            ),
        ),
        migrations.AlterField(
            model_name="umutientree",
            name="date_winjiriyeko",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 12, 14, 9, 16, 35, 832565, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="umutientreebackup",
            name="date_uzohererako",
            field=models.DateField(
                default=datetime.datetime(2024, 12, 14, 9, 16, 35, 833927)
            ),
        ),
        migrations.AlterField(
            model_name="umutientreebackup",
            name="date_winjiriyeko",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 12, 14, 9, 16, 35, 833886, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="umutisold",
            name="date_operation",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 12, 14, 9, 16, 35, 838141, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="usdtobif",
            name="effect_date",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 12, 14, 9, 16, 35, 840494, tzinfo=datetime.timezone.utc
                )
            ),
        ),
    ]
