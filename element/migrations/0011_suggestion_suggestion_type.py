# Generated by Django 3.1.1 on 2020-10-21 20:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('element', '0010_auto_20201021_2002'),
    ]

    operations = [
        migrations.AddField(
            model_name='suggestion',
            name='suggestion_type',
            field=models.CharField(default='aaa', max_length=10),
            preserve_default=False,
        ),
    ]
