# Generated by Django 4.1.3 on 2022-11-16 06:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pr', '0009_rename_pname_project_pmid'),
    ]

    operations = [
        migrations.CreateModel(
            name='SupervisorInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.TextField(unique=True)),
                ('eid', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='pr.employee')),
            ],
            options={
                'db_table': 'supervisorInfo',
            },
        ),
    ]
