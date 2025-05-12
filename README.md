# GameRank

A Django-based web application for discovering, scoring and discussing video games.

## Features

- Game discovery and ranking system
- User authentication with password-based login
- Game voting and following system
- Dynamic UI with HTMX
- XML and optional JSON API data import
- Responsive Bootstrap 5 design
- Configurable user preferences

## Setup

1. Create and activate a Python 3.12 virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create a superuser:
```bash
python manage.py createsuperuser
```

5. Import initial game data:
```bash
python manage.py import_listado1
```

6. Run the development server:
```bash
python manage.py runserver
```

## Testing

Run the test suite:
```bash
pytest
```

Run linters:
```bash
ruff check .
black --check .
mypy .
```

## Optional Features

The following features can be enabled via settings:

- FreeToGame API integration
- MMOBomb API integration
- Comment voting system
- Platform filtering
- Internationalization (i18n)
- Progressive Web App (PWA) support

To enable these features, set the corresponding `ENABLE_*` flags in `settings.py`.

## Project Structure

```
gamerank/
├── manage.py
├── gamerank/            # project settings
├── apps/
│   ├── core/           # games, votes, follows
│   ├── users/          # profile, custom auth
│   └── ingestion/      # XML & API import utilities
├── templates/
├── static/
└── tests/
``` 