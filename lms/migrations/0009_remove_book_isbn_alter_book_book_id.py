# Generated by Django 4.0.4 on 2022-04-25 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lms', '0008_alter_book_author_id_alter_book_category_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='book',
            name='isbn',
        ),
        migrations.AlterField(
            model_name='book',
            name='book_id',
            field=models.CharField(max_length=15, primary_key=True, serialize=False),
        ),
    ]
