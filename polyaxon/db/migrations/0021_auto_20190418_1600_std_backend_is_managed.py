# Generated by Django 2.2 on 2019-04-18 14:00

from django.db import migrations, models
import django.contrib.postgres.fields.jsonb
import libs.spec_validation


class Migration(migrations.Migration):
    dependencies = [
        ('db', '0020_auto_20190307_1611'),
    ]

    operations = [
        migrations.RenameField(
            model_name='buildjob',
            old_name='in_cluster',
            new_name='is_managed',
        ),
        migrations.RenameField(
            model_name='experiment',
            old_name='in_cluster',
            new_name='is_managed',
        ),
        migrations.RenameField(
            model_name='job',
            old_name='in_cluster',
            new_name='is_managed',
        ),
        migrations.RenameField(
            model_name='notebookjob',
            old_name='in_cluster',
            new_name='is_managed',
        ),
        migrations.RenameField(
            model_name='tensorboardjob',
            old_name='in_cluster',
            new_name='is_managed',
        ),
        migrations.AddField(
            model_name='job',
            name='backend',
            field=models.CharField(blank=True, default='native',
                                   help_text='The default backend use for running this entity.',
                                   max_length=16, null=True),
        ),
        migrations.AlterField(
            model_name='buildjob',
            name='backend',
            field=models.CharField(blank=True, default='native',
                                   help_text='The default backend use for running this entity.',
                                   max_length=16, null=True),
        ),
        migrations.AlterField(
            model_name='experiment',
            name='backend',
            field=models.CharField(blank=True, default='native',
                                   help_text='The default backend use for running this entity.',
                                   max_length=16, null=True),
        ),
        migrations.AddField(
            model_name='experimentgroup',
            name='backend',
            field=models.CharField(blank=True, default='native',
                                   help_text='The default backend use for running this entity.',
                                   max_length=16, null=True),
        ),
        migrations.AddField(
            model_name='pipeline',
            name='backend',
            field=models.CharField(blank=True, default='native',
                                   help_text='The default backend use for running this entity.',
                                   max_length=16, null=True),
        ),
        migrations.AlterField(
            model_name='buildjob',
            name='is_managed',
            field=models.BooleanField(default=True,
                                      help_text='If this entity is managed by the platform.'),
        ),
        migrations.AlterField(
            model_name='experiment',
            name='is_managed',
            field=models.BooleanField(default=True,
                                      help_text='If this entity is managed by the platform.'),
        ),
        migrations.AlterField(
            model_name='job',
            name='is_managed',
            field=models.BooleanField(default=True,
                                      help_text='If this entity is managed by the platform.'),
        ),
        migrations.AlterField(
            model_name='notebookjob',
            name='is_managed',
            field=models.BooleanField(default=True,
                                      help_text='If this entity is managed by the platform.'),
        ),
        migrations.AlterField(
            model_name='tensorboardjob',
            name='is_managed',
            field=models.BooleanField(default=True,
                                      help_text='If this entity is managed by the platform.'),
        ),
        migrations.AddField(
            model_name='experimentgroup',
            name='is_managed',
            field=models.BooleanField(default=True,
                                      help_text='If this entity is managed by the platform.'),
        ),
        migrations.AddField(
            model_name='pipeline',
            name='is_managed',
            field=models.BooleanField(default=True,
                                      help_text='If this entity is managed by the platform.'),
        ),
        migrations.AlterField(
            model_name='buildjob',
            name='config',
            field=django.contrib.postgres.fields.jsonb.JSONField(
                blank=True,
                help_text='The compiled polyaxonfile for the build job.',
                null=True, validators=[
                    libs.spec_validation.validate_build_spec_config]),
        ),
        migrations.AlterField(
            model_name='job',
            name='config',
            field=django.contrib.postgres.fields.jsonb.JSONField(
                blank=True,
                help_text='The compiled polyaxonfile for the run job.',
                null=True, validators=[
                    libs.spec_validation.validate_job_spec_config]),
        ),
    ]
