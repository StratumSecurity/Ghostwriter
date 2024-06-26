# Generated by Django 3.2.19 on 2024-05-16 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oplog', '0016_merge_20240429_1901'),
    ]

    operations = [
        migrations.RunSQL('SET CONSTRAINTS ALL IMMEDIATE', reverse_sql='SET CONSTRAINTS ALL DEFERRED'),
        migrations.AlterField(
            model_name='oplogentry',
            name='command',
            field=models.TextField(blank=True, default='', help_text='Provide the command you executed.', verbose_name='Command'),
        ),
        migrations.AlterField(
            model_name='oplogentry',
            name='comments',
            field=models.TextField(blank=True, default='', help_text='Any additional comments or useful information.', verbose_name='Comments'),
        ),
        migrations.AlterField(
            model_name='oplogentry',
            name='description',
            field=models.TextField(blank=True, default='', help_text='A description of why you executed the command.', verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='oplogentry',
            name='entry_identifier',
            field=models.CharField(blank=True, default='', help_text='Integrations may use this to track log entries.', max_length=65535, verbose_name='Identifier'),
        ),
        migrations.AlterField(
            model_name='oplogentry',
            name='output',
            field=models.TextField(blank=True, default='', help_text='The output of the executed command.', verbose_name='Output'),
        ),
        migrations.RunSQL('SET CONSTRAINTS ALL DEFERRED', reverse_sql='SET CONSTRAINTS ALL IMMEDIATE'),
    ]
