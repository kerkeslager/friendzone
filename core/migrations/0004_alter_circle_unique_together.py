# Generated by Django 5.0.1 on 2024-01-23 21:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_invitation_name'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='circle',
            unique_together={('name', 'owner')},
        ),
    ]
