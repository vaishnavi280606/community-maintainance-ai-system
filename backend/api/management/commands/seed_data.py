"""
Management command to seed the database with sample users and data.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed the database with sample users'

    def handle(self, *args, **options):
        # Create admin
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@community.com',
                password='admin123',
                first_name='Admin',
                last_name='User',
                role='admin',
                block='Admin Office',
            )
            self.stdout.write(self.style.SUCCESS('Created admin user'))

        # Create residents
        residents = [
            {'username': 'resident1', 'first_name': 'Rajesh', 'last_name': 'Kumar',
             'email': 'rajesh@community.com', 'block': 'Block A', 'flat_number': 'A-101'},
            {'username': 'resident2', 'first_name': 'Priya', 'last_name': 'Sharma',
             'email': 'priya@community.com', 'block': 'Block B', 'flat_number': 'B-205'},
            {'username': 'resident3', 'first_name': 'Amit', 'last_name': 'Patel',
             'email': 'amit@community.com', 'block': 'Block C', 'flat_number': 'C-302'},
        ]

        for res in residents:
            if not User.objects.filter(username=res['username']).exists():
                User.objects.create_user(
                    password='resident123',
                    role='resident',
                    **res
                )
                self.stdout.write(self.style.SUCCESS(f"Created resident: {res['username']}"))

        # Create technicians
        technicians = [
            {'username': 'tech_electrical', 'first_name': 'Suresh', 'last_name': 'Yadav',
             'email': 'suresh@community.com', 'specialization': 'Electrical'},
            {'username': 'tech_plumbing', 'first_name': 'Mohan', 'last_name': 'Das',
             'email': 'mohan@community.com', 'specialization': 'Plumbing'},
            {'username': 'tech_elevator', 'first_name': 'Ramesh', 'last_name': 'Singh',
             'email': 'ramesh@community.com', 'specialization': 'Elevator'},
            {'username': 'tech_general', 'first_name': 'Vijay', 'last_name': 'Nair',
             'email': 'vijay@community.com', 'specialization': 'Security,Cleanliness,Carpentry'},
        ]

        for tech in technicians:
            if not User.objects.filter(username=tech['username']).exists():
                User.objects.create_user(
                    password='tech123',
                    role='technician',
                    **tech
                )
                self.stdout.write(self.style.SUCCESS(f"Created technician: {tech['username']}"))

        self.stdout.write(self.style.SUCCESS('Database seeding complete!'))
        self.stdout.write('\nLogin credentials:')
        self.stdout.write('  Admin:      admin / admin123')
        self.stdout.write('  Resident:   resident1 / resident123')
        self.stdout.write('  Technician: tech_electrical / tech123')
