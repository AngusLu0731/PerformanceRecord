# Generated by Django 4.1.3 on 2022-11-16 03:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pr', '0007_project_pname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectpr',
            name='belongProject',
            field=models.TextField(unique=True),
        ),
    ]
