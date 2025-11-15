"""
Management command to start the price updater manually
"""
from django.core.management.base import BaseCommand
from market.price_scheduler import start_price_scheduler


class Command(BaseCommand):
    help = 'Start the background price updater'

    def handle(self, *args, **options):
        self.stdout.write('Starting price updater...')
        start_price_scheduler()
        self.stdout.write(self.style.SUCCESS('Price updater started!'))
        self.stdout.write('Press Ctrl+C to stop...')
        
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\nStopping price updater...'))
            from market.price_scheduler import stop_price_scheduler
            stop_price_scheduler()
            self.stdout.write(self.style.SUCCESS('Price updater stopped.'))

