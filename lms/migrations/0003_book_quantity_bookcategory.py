# Generated by Django 4.0.4 on 2022-04-24 13:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lms', '0002_alter_category_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='quantity',
            field=models.IntegerField(default=0),
        ),
        migrations.CreateModel(
            name='BookCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('book_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='book_category', to='lms.book')),
                ('category_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='book_category', to='lms.category')),
            ],
        ),
    ]
