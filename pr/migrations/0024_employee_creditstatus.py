# Generated by Django 4.1.3 on 2022-11-25 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pr', '0023_alter_supervisorinfo_dept_alter_supervisorinfo_eid'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='creditStatus',
            field=models.TextField(default=1),
            preserve_default=False,
        ),
    ]
