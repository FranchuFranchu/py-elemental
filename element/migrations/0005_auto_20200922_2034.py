# Generated by Django 3.0.5 on 2020-09-22 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('element', '0004_auto_20200908_2242'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='suggestion',
            name='ingredients',
        ),
        migrations.AddField(
            model_name='suggestion',
            name='ingredients',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='suggestion',
            name='name',
            field=models.TextField(),
        ),
    ]
