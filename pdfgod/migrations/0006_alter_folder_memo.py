# Generated by Django 5.0.4 on 2024-05-13 01:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pdfgod', '0005_folder_memo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='folder',
            name='memo',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
