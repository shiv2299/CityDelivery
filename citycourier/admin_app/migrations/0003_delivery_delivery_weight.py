# Generated by Django 3.0.6 on 2020-05-15 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_app', '0002_delivery_delivery_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='delivery',
            name='delivery_weight',
            field=models.FloatField(null=True),
        ),
    ]
