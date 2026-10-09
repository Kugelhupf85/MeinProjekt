# Generated manually for Arcanovi Permissions App

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('core_user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('permission_type', models.CharField(choices=[('view', 'View'), ('edit', 'Edit'), ('delete', 'Delete'), ('admin', 'Admin')], help_text='Type of permission granted', max_length=20)),
                ('resource_type', models.CharField(choices=[('world', 'World'), ('adventure', 'Adventure'), ('character', 'Character'), ('rule_set', 'Rule Set')], help_text='Type of resource this permission applies to', max_length=20)),
                ('object_id', models.PositiveIntegerField(help_text='ID of the resource')),
                ('granted_at', models.DateTimeField(auto_now_add=True, help_text='When this permission was granted')),
                ('is_active', models.BooleanField(default=True, help_text='Whether this permission is currently active')),
                ('expires_at', models.DateTimeField(blank=True, help_text='When this permission expires (optional)', null=True)),
                ('notes', models.TextField(blank=True, help_text='Additional notes about this permission')),
                ('content_type', models.ForeignKey(help_text='Content type of the resource', on_delete=django.db.models.deletion.CASCADE, related_name='arcanovi_permissions', to='contenttypes.contenttype')),
                ('granted_by', models.ForeignKey(blank=True, help_text='User who granted this permission', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='granted_permissions', to='core_user.user')),
                ('user', models.ForeignKey(help_text='The user who has this permission', on_delete=django.db.models.deletion.CASCADE, related_name='permissions', to='core_user.user')),
            ],
            options={
                'verbose_name': 'Permission',
                'verbose_name_plural': 'Permissions',
                'db_table': 'permissions_permission',
                'ordering': ['user', 'resource_type', 'permission_type'],
                'unique_together': {('user', 'content_type', 'object_id', 'permission_type')},
            },
        ),
        migrations.CreateModel(
            name='PermissionLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('log_type', models.CharField(choices=[('check', 'Permission Check'), ('grant', 'Permission Granted'), ('revoke', 'Permission Revoked'), ('failed', 'Failed Permission Attempt'), ('inheritance', 'Permission Inheritance'), ('bulk', 'Bulk Permission Operation')], help_text='Type of permission activity', max_length=20)),
                ('timestamp', models.DateTimeField(auto_now_add=True, help_text='When this log entry was created')),
                ('resource_type', models.CharField(help_text='Type of resource involved', max_length=20)),
                ('resource_id', models.PositiveIntegerField(help_text='ID of the resource involved')),
                ('permission_type', models.CharField(help_text='Type of permission involved', max_length=20)),
                ('success', models.BooleanField(default=True, help_text='Whether the permission operation was successful')),
                ('details', models.JSONField(blank=True, help_text='Additional details about the operation', null=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, help_text='IP address of the request', null=True)),
                ('user_agent', models.TextField(blank=True, help_text='User agent of the request')),
                ('request_path', models.CharField(blank=True, help_text='Request path', max_length=255)),
                ('user', models.ForeignKey(help_text='User involved in the permission activity', on_delete=django.db.models.deletion.CASCADE, related_name='permission_logs', to='core_user.user')),
            ],
            options={
                'verbose_name': 'Permission Log',
                'verbose_name_plural': 'Permission Logs',
                'db_table': 'permissions_permissionlog',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.AddIndex(
            model_name='permission',
            index=models.Index(fields=['user', 'resource_type'], name='permissions_user_id_b3949c_idx'),
        ),
        migrations.AddIndex(
            model_name='permission',
            index=models.Index(fields=['content_type', 'object_id'], name='permissions_content_bf8c6c_idx'),
        ),
        migrations.AddIndex(
            model_name='permission',
            index=models.Index(fields=['permission_type'], name='permissions_permiss_da3fc1_idx'),
        ),
        migrations.AddIndex(
            model_name='permission',
            index=models.Index(fields=['is_active'], name='permissions_is_acti_9afbb7_idx'),
        ),
        migrations.AddIndex(
            model_name='permissionlog',
            index=models.Index(fields=['user'], name='permissions_user_id_65cee6_idx'),
        ),
        migrations.AddIndex(
            model_name='permissionlog',
            index=models.Index(fields=['resource_type', 'resource_id'], name='permissions_resourc_8a0a88_idx'),
        ),
        migrations.AddIndex(
            model_name='permissionlog',
            index=models.Index(fields=['log_type'], name='permissions_log_typ_454215_idx'),
        ),
        migrations.AddIndex(
            model_name='permissionlog',
            index=models.Index(fields=['timestamp'], name='permissions_timesta_a7a6d0_idx'),
        ),
        # Test models for permission testing
        migrations.CreateModel(
            name='TestWorld',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
            ],
            options={
                'db_table': 'test_world',
            },
        ),
        migrations.CreateModel(
            name='TestAdventure',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
            ],
            options={
                'db_table': 'test_adventure',
            },
        ),
    ] 