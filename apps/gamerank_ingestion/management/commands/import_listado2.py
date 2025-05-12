import json
from datetime import datetime
from typing import Dict, Any, Optional
from django.core.management.base import BaseCommand
from django.db import transaction
import requests
from apps.gamerank_core.models import Game


class Command(BaseCommand):
    help = 'Import games from listado2.json API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            type=str,
            default='https://api.example.com/listado2.json',
            help='URL of the JSON API (default: https://api.example.com/listado2.json)'
        )

    def handle(self, *args: tuple, **options: Dict[str, Any]) -> None:
        url = options['url']
        self.stdout.write(f'Importing games from {url}...')

        try:
            response = requests.get(url)
            response.raise_for_status()
            games_data = response.json()
        except requests.RequestException as e:
            self.stderr.write(
                self.style.ERROR(f'Error fetching data from API: {str(e)}')
            )
            return
        except json.JSONDecodeError:
            self.stderr.write(
                self.style.ERROR('Invalid JSON response from API')
            )
            return

        games_created = 0
        games_updated = 0

        with transaction.atomic():
            for game_data in games_data:
                try:
                    game_id = f"LIS2-{game_data['id']}"
                    
                    game, created = Game.objects.update_or_create(
                        id=game_id,
                        defaults={
                            'title': game_data['title'],
                            'platform': game_data['platform'],
                            'genre': game_data['genre'],
                            'developer': game_data['developer'],
                            'publisher': game_data['publisher'],
                            'release_date': datetime.strptime(
                                game_data['release_date'],
                                '%Y-%m-%d'
                            ).date(),
                            'description': game_data['description'],
                            'image_url': game_data['image_url'],
                            'source': 'LIS2',
                        }
                    )

                    if created:
                        games_created += 1
                    else:
                        games_updated += 1

                except (KeyError, ValueError) as e:
                    self.stderr.write(
                        self.style.WARNING(f'Error processing game: {str(e)}')
                    )
                    continue

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully imported {games_created} new games and updated {games_updated} existing games'
            )
        ) 