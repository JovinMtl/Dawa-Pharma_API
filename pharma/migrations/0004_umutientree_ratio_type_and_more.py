# Generated by Django 5.0.4 on 2024-04-26 09:52

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pharma", "0003_alter_umutientree_date_uzohererako_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="umutientree",
            name="ratio_type",
            field=models.FloatField(default=1),
        ),
        migrations.AlterField(
            model_name="umutientree",
            name="date_uzohererako",
            field=models.DateField(
                default=datetime.datetime(2024, 4, 26, 9, 52, 26, 879246)
            ),
        ),
        migrations.AlterField(
            model_name="umutientree",
            name="date_winjiriyeko",
            field=models.DateField(
                default=datetime.datetime(2024, 4, 26, 9, 52, 26, 879137)
            ),
        ),
        migrations.AlterField(
            model_name="umutientree",
            name="type_umuti",
            field=models.CharField(
                default="null", max_length=10, verbose_name="Ni Flacon canke plaquette,"
            ),
        ),
    ]
