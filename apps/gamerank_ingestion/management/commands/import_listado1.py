import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Optional, Dict, Any
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.gamerank_core.models import Game


class Command(BaseCommand):
    help = 'Import games from listado1.xml file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='listado1.xml',
            help='Path to the XML file (default: listado1.xml)'
        )

    def handle(self, *args: tuple, **options: Dict[str, Any]) -> None:
        file_path = options['file']
        self.stdout.write(f'Importing games from {file_path}...')

        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f'File not found: {file_path}'))
            return
        except ET.ParseError:
            self.stderr.write(self.style.ERROR(f'Invalid XML file: {file_path}'))
            return

        games_created = 0
        games_updated = 0
        games_skipped = 0

        with transaction.atomic():
            for game_elem in root.findall('.//game'):
                game_data = self._parse_game_element(game_elem)
                
                if game_data is None:
                    games_skipped += 1
                    continue # Skip this game if parsing failed
                    
                game_id = f"LIS1-{game_data['id']}"
                
                try:
                    game, created = Game.objects.update_or_create(
                        id=game_id,
                        defaults={
                            'title': game_data['title'],
                            'platform': game_data['platform'],
                            'genre': game_data['genre'],
                            'developer': game_data['developer'],
                            'publisher': game_data['publisher'],
                            'release_date': game_data['release_date'],
                            'description': game_data['description'],
                            'image_url': game_data['image_url'],
                            'source': 'LIS1',
                        }
                    )

                    if created:
                        games_created += 1
                    else:
                        games_updated += 1

                except Exception as e: # Catch potential DB errors too
                    self.stderr.write(
                        self.style.WARNING(f"Error saving game ID '{game_id}': {str(e)}")
                    )
                    games_skipped += 1
                    continue

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully imported {games_created} new games, updated {games_updated} existing games, and skipped {games_skipped} games.'
            )
        )

    def _parse_game_element(self, game_elem: ET.Element) -> Optional[Dict[str, Any]]:
        """Parse a game element from the XML file, returning None if required fields are missing."""
        
        def get_text(tag_name: str) -> Optional[str]:
            element = game_elem.find(tag_name)
            return element.text if element is not None else None
        
        # Use short_description for our description field
        description = get_text('short_description')
        # Use thumbnail for image_url
        image_url = get_text('thumbnail') 
        game_id = get_text('id')
        title = get_text('title')
        platform = get_text('platform')
        genre = get_text('genre')
        developer = get_text('developer')
        publisher = get_text('publisher')
        release_date_str = get_text('release_date')

        # Check for missing required fields
        required_fields = {
            'id': game_id,
            'title': title,
            'platform': platform,
            'genre': genre,
            'developer': developer,
            'publisher': publisher,
            'release_date': release_date_str,
            'description': description,
            'image_url': image_url,
        }
        
        missing = [name for name, value in required_fields.items() if value is None]
        if missing:
            self.stderr.write(
                self.style.WARNING(f"Skipping game ID '{game_id or 'UNKNOWN'}': Missing fields: {', '.join(missing)}")
            )
            return None
            
        # Parse release date
        try:
            release_date = datetime.strptime(release_date_str, '%Y-%m-%d').date()
        except ValueError:
             self.stderr.write(
                self.style.WARNING(f"Skipping game ID '{game_id}': Invalid date format '{release_date_str}'")
            )
             return None

        return {
            'id': game_id,
            'title': title,
            'platform': platform,
            'genre': genre,
            'developer': developer,
            'publisher': publisher,
            'release_date': release_date,
            'description': description,
            'image_url': image_url,
        } 