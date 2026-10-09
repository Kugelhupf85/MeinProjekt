"""
Management command to create a demo superuser with all security features.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.core_user.models import User, SecurityQuestion, UserSecurityAnswer


class Command(BaseCommand):
    help = 'Create a demo superuser with security questions for testing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default='admin@arcanovi.com',
            help='Email for the superuser'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin123',
            help='Password for the superuser'
        )
        parser.add_argument(
            '--first-name',
            type=str,
            default='Dungeon',
            help='First name for the superuser'
        )
        parser.add_argument(
            '--last-name',
            type=str,
            default='Master',
            help='Last name for the superuser'
        )
    
    @transaction.atomic
    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(f'User with email {email} already exists')
            )
            return
        
        # Create superuser
        user = User.objects.create_superuser(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Superuser created: {user.email}')
        )
        
        # Set up security questions with demo answers
        security_data = [
            {
                'question_text': 'Wie heißt Ihr erster Pen-and-Paper-Charakter?',
                'answer': 'Gandalf'
            },
            {
                'question_text': 'Welches war Ihr erstes Rollenspielsystem?',
                'answer': 'DSA'
            },
            {
                'question_text': 'Wie heißt Ihr Lieblings-Spielmeister/DM?',
                'answer': 'Tolkien'
            }
        ]
        
        created_answers = 0
        for data in security_data:
            try:
                question = SecurityQuestion.objects.get(
                    question_text=data['question_text'],
                    is_active=True
                )
                
                # Create security answer
                security_answer = UserSecurityAnswer.objects.create(
                    user=user,
                    question=question
                )
                security_answer.set_answer(data['answer'])
                created_answers += 1
                
            except SecurityQuestion.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f'Security question not found: {data["question_text"]}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Created {created_answers} security answers for user'
            )
        )
        
        # Display summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('DEMO SUPERUSER CREATED'))
        self.stdout.write('='*50)
        self.stdout.write(f'Email: {email}')
        self.stdout.write(f'Password: {password}')
        self.stdout.write(f'Name: {first_name} {last_name}')
        self.stdout.write(f'Security Questions: {created_answers}')
        self.stdout.write(f'Email Verified: {user.is_email_verified}')
        self.stdout.write('='*50)
        self.stdout.write('\nSecurity Question Answers:')
        for data in security_data[:created_answers]:
            self.stdout.write(f'- {data["question_text"]} → {data["answer"]}')
        self.stdout.write('='*50) 