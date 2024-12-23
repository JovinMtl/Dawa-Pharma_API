# Generated by Django 5.0.4 on 2024-12-23 15:43

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pharma", "0054_alter_imitiset_date_last_vente_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bondecommande",
            name="num_du_bon",
            field=models.CharField(default="0000", max_length=10, unique=True),
        ),
        migrations.AlterField(
            model_name="imitiset",
            name="date_last_vente",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 12, 23, 15, 43, 22, 582533, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="imitisuggest",
            name="previous_date",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 12, 23, 15, 43, 22, 586888, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="umutientree",
            name="date_entrant",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 12, 23, 15, 43, 22, 579132, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="umutientree",
            name="date_peremption",
            field=models.DateField(
                default=datetime.datetime(2024, 12, 23, 15, 43, 22, 579205)
            ),
        ),
        migrations.AlterField(
            model_name="umutientreebackup",
            name="date_entrant",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 12, 23, 15, 43, 22, 580734, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="umutientreebackup",
            name="date_peremption",
            field=models.DateField(
                default=datetime.datetime(2024, 12, 23, 15, 43, 22, 580780)
            ),
        ),
        migrations.AlterField(
            model_name="umutisold",
            name="date_operation",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 12, 23, 15, 43, 22, 585119, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="usdtobif",
            name="effect_date",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 12, 23, 15, 43, 22, 587567, tzinfo=datetime.timezone.utc
                )
            ),
        ),
    ]
