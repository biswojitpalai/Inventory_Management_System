# Generated by Django 5.1.2 on 2025-01-17 17:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0010_item'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Item',
        ),
    ]
