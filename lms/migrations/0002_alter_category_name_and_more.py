# Generated by Django 4.0.4 on 2022-04-24 08:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lms', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AddIndex(
            model_name='author',
            index=models.Index(fields=['name'], name='lms_author_name_d3b850_idx'),
        ),
        migrations.AddIndex(
            model_name='publisher',
            index=models.Index(fields=['name'], name='lms_publish_name_c05509_idx'),
        ),
    ]
