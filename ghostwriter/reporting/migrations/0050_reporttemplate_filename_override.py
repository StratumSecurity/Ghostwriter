# Generated by Django 3.2.19 on 2024-04-22 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0049_auto_20240315_1744'),
    ]

    operations = [
        migrations.AddField(
            model_name='reporttemplate',
            name='filename_override',
            field=models.CharField(blank=True, default='', help_text='Jinja2 template. All template variables are available, plus {{now}} and {{company_name}}. The file extension is added to this. If blank, the admin-provided default will be used.', max_length=255, verbose_name='Filename Template'),
        ),
    ]