# Generated by Django 3.0.5 on 2020-09-22 20:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('element', '0005_auto_20200922_2034'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='ingredients',
        ),
        migrations.RemoveField(
            model_name='suggestion',
            name='ingredients',
        ),
    ]
