# Generated by Django 5.0.1 on 2024-02-12 22:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_user_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.ImageField(blank=True, height_field='avatar_height', null=True, upload_to='', width_field='avatar_width'),
        ),
    ]
