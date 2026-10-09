"""
Management command to create an admin user with DungeonMaster profile.
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from ...models import DungeonMaster, UserSettings, UserKeys


class Command(BaseCommand):
    help = 'Create an admin user with DungeonMaster profile and superuser privileges'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Username for the admin user (default: admin)'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@arcanovi.com',
            help='Email for the admin user (default: admin@arcanovi.com)'
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Password for the admin user (if not provided, will use environment variable ADMIN_PASSWORD)'
        )
        parser.add_argument(
            '--display-name',
            type=str,
            default='System Administrator',
            help='Display name for the admin user (default: System Administrator)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force creation even if user already exists (will update existing user)'
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password'] or os.environ.get('ADMIN_PASSWORD')
        display_name = options['display_name']
        force = options['force']

        if not password:
            self.stdout.write(
                self.style.ERROR(
                    'Password is required. Provide it via --password or set ADMIN_PASSWORD environment variable.'
                )
            )
            return

        try:
            with transaction.atomic():
                # Check if user already exists
                user_exists = User.objects.filter(username=username).exists()
                
                if user_exists and not force:
                    self.stdout.write(
                        self.style.ERROR(
                            f'User "{username}" already exists. Use --force to update existing user.'
                        )
                    )
                    return

                if user_exists:
                    # Update existing user
                    user = User.objects.get(username=username)
                    user.email = email
                    user.set_password(password)
                    user.is_staff = True
                    user.is_superuser = True
                    user.is_active = True
                    user.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'Updated existing user "{username}"')
                    )
                else:
                    # Create new user
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        is_staff=True,
                        is_superuser=True,
                        is_active=True
                    )
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'Created new user "{username}"')
                    )

                # Create or update DungeonMaster profile
                dungeon_master, created = DungeonMaster.objects.get_or_create(
                    user=user,
                    defaults={
                        'display_name': display_name,
                        'bio': 'System Administrator - Full access to all Arcanovi features',
                        'experience_level': 'master',
                        'strictness_level': 5,
                        'green_flags': ['system_admin', 'full_access'],
                        'red_flags': [],
                        'content_rating': 'mature',
                        'themes_preferences': ['administration', 'system_management'],
                        'is_active': True,
                        'is_public': False,
                    }
                )

                if not created:
                    # Update existing DungeonMaster profile
                    dungeon_master.display_name = display_name
                    dungeon_master.bio = 'System Administrator - Full access to all Arcanovi features'
                    dungeon_master.experience_level = 'master'
                    dungeon_master.is_active = True
                    dungeon_master.save()

                # Create or get UserSettings
                settings, settings_created = UserSettings.objects.get_or_create(
                    dungeonmaster=dungeon_master,
                    defaults={
                        'ui_settings': {
                            'theme': 'dark',
                            'language': 'de',
                            'admin_mode': True,
                            'show_advanced_options': True
                        },
                        'ai_settings': {
                            'enabled': True,
                            'admin_access': True
                        },
                        'feature_flags': {
                            'admin_panel': True,
                            'system_management': True,
                            'user_management': True,
                            'beta_features': True
                        },
                        'privacy_settings': {
                            'profile_visibility': 'admin_only',
                            'data_access': 'full'
                        }
                    }
                )

                # Create or get UserKeys
                keys, keys_created = UserKeys.objects.get_or_create(
                    dungeonmaster=dungeon_master,
                    defaults={
                        'security_notes': 'System Administrator - Full API access'
                    }
                )

                # Output summary
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\n✅ Admin user setup completed successfully!'
                    )
                )
                self.stdout.write(f'   👤 Username: {username}')
                self.stdout.write(f'   📧 Email: {email}')
                self.stdout.write(f'   🎭 Display Name: {display_name}')
                self.stdout.write(f'   🆔 Entity ID: {dungeon_master.entity_id}')
                self.stdout.write(f'   🔑 Superuser: Yes')
                self.stdout.write(f'   🛡️  Staff: Yes')
                self.stdout.write(f'   🎮 DungeonMaster Profile: {"Updated" if not created else "Created"}')
                self.stdout.write(f'   ⚙️  Settings: {"Updated" if not settings_created else "Created"}')
                self.stdout.write(f'   🔐 API Keys: {"Updated" if not keys_created else "Created"}')
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\n🚀 Admin user is ready! You can now login with username "{username}"'
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating admin user: {str(e)}')
            )
            raise 