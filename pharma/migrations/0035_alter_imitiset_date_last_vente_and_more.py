# Generated by Django 4.2.16 on 2024-11-27 11:42

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pharma', '0034_remove_umutientree_difference_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imitiset',
            name='date_last_vente',
            field=models.DateTimeField(default=datetime.datetime(2024, 11, 27, 11, 42, 47, 553914, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='imitisuggest',
            name='previous_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 11, 27, 11, 42, 47, 557529, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='umutientree',
            name='date_uzohererako',
            field=models.DateField(default=datetime.datetime(2024, 11, 27, 11, 42, 47, 550231)),
        ),
        migrations.AlterField(
            model_name='umutientree',
            name='date_winjiriyeko',
            field=models.DateTimeField(default=datetime.datetime(2024, 11, 27, 11, 42, 47, 550161, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='umutientreebackup',
            name='date_uzohererako',
            field=models.DateField(default=datetime.datetime(2024, 11, 27, 11, 42, 47, 552143)),
        ),
        migrations.AlterField(
            model_name='umutientreebackup',
            name='date_winjiriyeko',
            field=models.DateTimeField(default=datetime.datetime(2024, 11, 27, 11, 42, 47, 552106, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='umutisold',
            name='date_operation',
            field=models.DateTimeField(default=datetime.datetime(2024, 11, 27, 11, 42, 47, 555541, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='usdtobif',
            name='effect_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 11, 27, 11, 42, 47, 558817, tzinfo=datetime.timezone.utc)),
        ),
    ]
