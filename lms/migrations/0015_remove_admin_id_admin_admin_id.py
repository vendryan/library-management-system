# Generated by Django 4.0.4 on 2022-05-26 04:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lms', '0014_admin'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='admin',
            name='id',
        ),
        migrations.AddField(
            model_name='admin',
            name='admin_id',
            field=models.AutoField(default=1, primary_key=True, serialize=False),
            preserve_default=False,
        ),
    ]
