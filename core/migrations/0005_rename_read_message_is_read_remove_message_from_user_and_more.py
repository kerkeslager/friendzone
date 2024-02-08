# Generated by Django 5.0.1 on 2024-02-08 17:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_connection_circles'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='read',
            new_name='is_read',
        ),
        migrations.RemoveField(
            model_name='message',
            name='from_user',
        ),
        migrations.AlterField(
            model_name='message',
            name='connection',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outgoing_messages', to='core.connection'),
        ),
    ]
