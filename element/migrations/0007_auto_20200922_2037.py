# Generated by Django 3.0.5 on 2020-09-22 20:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('element', '0006_auto_20200922_2036'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='suggestion',
            name='ingredients',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
