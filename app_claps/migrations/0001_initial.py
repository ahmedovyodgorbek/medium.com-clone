# Generated by Django 5.1.6 on 2025-02-25 17:15

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('app_comments', '0001_initial'),
        ('app_posts', '0007_remove_postclapsmodel_post_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PostClapsModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='claps', to='app_posts.postsmodel')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='post_claps', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'post clap',
                'verbose_name_plural': 'post claps',
            },
        ),
        migrations.CreateModel(
            name='PostCommentClapsModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='claps', to='app_comments.postcommentsmodel')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='comment_claps', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'comment clap',
                'verbose_name_plural': 'comment claps',
            },
        ),
    ]
