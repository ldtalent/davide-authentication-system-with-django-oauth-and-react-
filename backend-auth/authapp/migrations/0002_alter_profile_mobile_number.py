# Generated by Django 4.2.3 on 2023-07-09 01:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='mobile_number',
            field=models.CharField(max_length=20),
        ),
    ]