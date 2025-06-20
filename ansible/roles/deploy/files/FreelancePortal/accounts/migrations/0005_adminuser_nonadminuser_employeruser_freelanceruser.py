# Generated by Django 4.2.20 on 2025-03-14 18:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_employerprofile_jobs_active_employerprofile_spent'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminUser',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('accounts.customuser',),
        ),
        migrations.CreateModel(
            name='NonAdminUser',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('accounts.customuser',),
        ),
        migrations.CreateModel(
            name='EmployerUser',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('accounts.nonadminuser',),
        ),
        migrations.CreateModel(
            name='FreelancerUser',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('accounts.nonadminuser',),
        ),
    ]
