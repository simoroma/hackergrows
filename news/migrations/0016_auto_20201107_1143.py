# Generated by Django 3.1 on 2020-11-07 11:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0015_story_product_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='story',
            name='duplicate_of',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='news.story'),
        ),
    ]
