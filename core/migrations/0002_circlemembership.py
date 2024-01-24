# Generated by Django 5.0.1 on 2024-01-24 19:38

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CircleMembership',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('circle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='circle_memberships', to='core.circle')),
                ('connection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='circle_memberships', to='core.connection')),
            ],
        ),
    ]
