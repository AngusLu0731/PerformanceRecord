# Generated by Django 4.1.3 on 2022-11-16 02:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pr', '0004_remove_normalpr_content_normalpr_content1_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='doneProjectPR',
            field=models.IntegerField(),
        ),
    ]