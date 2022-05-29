# Generated by Django 4.0.4 on 2022-04-24 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lms', '0005_remove_book_author_id_remove_book_category_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='author_id',
            field=models.ManyToManyField(related_name='books', to='lms.author'),
        ),
        migrations.AddField(
            model_name='book',
            name='category_id',
            field=models.ManyToManyField(related_name='books', to='lms.category'),
        ),
    ]