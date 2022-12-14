# Generated by Django 4.1.3 on 2022-11-25 12:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pr', '0026_remove_employee_dasdsa'),
    ]

    operations = [
        migrations.CreateModel(
            name='CreditRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receiver', models.TextField()),
                ('grade', models.TextField()),
                ('credit', models.TextField()),
                ('giver', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='pr.employee')),
            ],
            options={
                'db_table': 'creditRecord',
            },
        ),
        migrations.CreateModel(
            name='CreditDistribution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receiveDept', models.TextField()),
                ('creditDept', models.TextField()),
                ('giveDept', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='pr.order')),
            ],
            options={
                'db_table': 'creditDistribution',
            },
        ),
    ]
