# Generated by Django 2.1.5 on 2019-02-06 14:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wargame', '0011_file_config_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='challenge',
            name='tags',
        ),
        migrations.DeleteModel(
            name='Tag',
        ),
    ]
