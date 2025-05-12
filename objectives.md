## GameRank – Developer Instruction Document

*(focus: Python 3 + Django only – deployment & repo hosting out of scope)*

---

### 1. Introduction

GameRank is a web application for discovering, scoring and discussing video-games.
These instructions translate the functional brief into a concrete **development-first plan** aimed at one or more software engineers who will build the Django code-base. The goal is to deliver a clean, test-covered project that satisfies the mandatory features, supports optional extensions, and remains easy to maintain.

---

### 2. High-level objectives

| # | Objective                                                                                         | Success indicator                                          |
| - | ------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| 1 | **Import games** from the XML file *listado1.xml* and (optionally) public JSON APIs               | Games appear in DB with unique IDs and all required fields |
| 2 | **CRUD + ranking UI** for games, comments, votes, follows                                         | Pages render correctly, rankings update instantly          |
| 3 | **Session authentication** with password table & custom login flow                                | All non-home URLs redirect to login without session        |
| 4 | **Dynamic UX with HTMX** on the game detail (auto-refresh comments, inline forms, no full reload) | JS-less fallback still works                               |
| 5 | **User personal area** (votes, follows, profile settings)                                         | Counts, lists and configuration reflected in DB & UI       |
| 6 | **Admin site accessibility** for all models                                                       | Staff can manage data via `/admin/`                        |
| 7 | **Comprehensive tests** (E2E mandatory, unit optional)                                            | `pytest` suite green in CI                                 |
| 8 | **Clean architecture & styling** (templates hierarchy, Bootstrap layout, configurable fonts)      | Code passes linters; pages responsive                      |

---

#### 2.1 Data sources:

- Listado 1 (listado1.xml)
- Free-To-game (https://www.freetogame.com/api/games)
- MMO Games API - By MMOBomb (https://www.mmobomb.com/api1/games)

### 3. Technical stack & key dependencies

| Concern          | Library / Tool                               | Notes                                     |
| ---------------- | -------------------------------------------- | ----------------------------------------- |
| Core framework   | **Django 5.x**                               | Use the LTS available at project start    |
| Dynamic partials | **django-htmx**                              | Thin wrapper over HTMX                    |
| Forms            | **django-crispy-forms** (bootstrap5 backend) | Consistent markup                         |
| Testing          | **pytest-django**, **pytest-selenium**       | Use ChromeDriver in headless mode for E2E |
| Lint / format    | **ruff**, **black**, **isort**, **mypy**     | Enforce via pre-commit                    |
| Optional tasks   | **Celery + Redis**                           | Only if periodic API sync is implemented  |

---

### 4. Project skeleton

```text
gamerank/
├── manage.py
├── gamerank/            # project settings
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── apps/
│   ├── core/            # games, votes, follows
│   ├── users/           # profile, custom auth
│   └── ingestion/       # XML & API import utilities
├── templates/
│   ├── _base.html
│   ├── _navbar.html
│   ├── _footer.html
│   └── ...
├── static/
│   ├── css/
│   └── js/
├── tests/
│   ├── e2e/
│   └── unit/
└── requirements.txt
```

---

### 5. Detailed development plan

#### 5.1  Day-1 setup

| Step | Action                                                                         |
| ---- | ------------------------------------------------------------------------------ |
| 1    | Create Python 3.12 virtual-env, install Django, lock versions with `pip-tools` |
| 2    | `django-admin startproject gamerank && cd gamerank`                            |
| 3    | Add **ruff**, **black**, **isort**, **pre-commit** hooks                       |
| 4    | Initialise git (remote added later)                                            |

---

#### 5.2  Core domain (apps/core)

| Model     | Fields (key ones)                                                                                                                                                        | Behaviour / signals                                       |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------- |
| `Game`    | `id` (CharField, pk) – must store prefix (`LIS1-`, etc.)<br>`title`, `platform`, `genre`, `developer`, `publisher`, `release_date`, `description`, `image_url`, `source` | `average_score` & `votes_count` calculated via annotation |
| `Vote`    | FK `user`, FK `game`, `score` (Integer 0-5), `created`                                                                                                                   | Unique `(user, game)` constraint                          |
| `Follow`  | FK `user`, FK `game`, `created`                                                                                                                                          | Unique `(user, game)`                                     |
| `Comment` | FK `user`, FK `game`, `body`, `created` (auto\_now\_add)                                                                                                                 | —                                                         |

Add `@property` helpers on `User` model (via `users` app) to compute total votes, avg score, etc.

---

#### 5.3  Custom authentication (apps/users)

1. **Password table**

   ```python
   class SitePassword(models.Model):
       value = models.CharField(max_length=128, unique=True)
   ```
2. **Login view**
   *Template-powered* form that checks provided password against `SitePassword`.
   On success: create session cookie (`request.session['auth'] = True`).
   Middleware to protect all views except home + login.
3. **Profile settings**
   Model `UserProfile` (O2O with Django `User`) storing alias, font\_family, font\_size.

---

#### 5.4  Ingestion utilities (apps/ingestion)

| Component                                       | Details                                                                                                    |
| ----------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| Management command `import_listado1`            | Fetch XML via `requests`, parse with `xml.etree` or `lxml`, create/update `Game` rows. Use prefix `LIS1-`. |
| Generic command `import_ftg` & `import_mmobomb` | Similar, but for JSON APIs, configurable `source_prefix`.                                                  |
| Deduplication                                   | `Game.id` is pk, so re-running import is idempotent.                                                       |
| Optional                                        | Celery periodic task to refresh APIs daily.                                                                |

---


#### 5.5  Views, URLs & templates

| URL                | View class                | Template              | Notes                                     |
| ------------------ | ------------------------- | --------------------- | ----------------------------------------- |
| `/`                | `GameListView` (ListView) | `home.html`           | Order by `average_score` desc             |
| `/game/<id>/`      | `GameDetailView`          | `game_detail.html`    | Shows all info + forms                    |
| `/game/<id>/htmx/` | `GameDetailHTMXView`      | `partials/*`          | HTMX endpoints for comments, preview etc. |
| `/user/`           | `UserDashboardView`       | `user_dashboard.html` |                                           |
| `/user/votes/`     | `UserVotesView`           | `user_votes.html`     |                                           |
| `/user/follows/`   | `UserFollowsView`         | `user_follows.html`   |                                           |
| `/settings/`       | `UserSettingsView`        | `settings.html`       |                                           |
| `/help/`           | StaticTemplateView        | `help.html`           |                                           |

**Template hierarchy**
`_base.html` → includes `_navbar.html` and `_footer.html`; content blocks: `title`, `content`, `extra_js`.

Use **Bootstrap 5** grid; toggle dark/light fonts via CSS vars influenced by user settings.

---

#### 5.6  JSON endpoint

`/game/<id>.json` – Function-based view returning `GameSerializer(game).json()` where serializer includes comment count.

---

#### 5.7  Static assets & configuration

* Place fonts in `static/fonts/`, define CSS classes driven by user profile (`body { font-family: var(--font); font-size: var(--size); }`).
* Use `collectstatic` for later deployment but keep in mind only.

---

#### 5.8  Testing strategy

| Layer       | Tooling                                        | Coverage targets                                                                                                       |
| ----------- | ---------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Unit        | `pytest-django`                                | Models: validation, computed props<br>Views: HTTP 302 on unauth, 200 on auth                                           |
| Integration | *None* – simple project, unit + e2e sufficient |                                                                                                                        |
| E2E         | `pytest-selenium` + headless Chrome            | At least one path per resource type:<br>• Login flow<br>• Vote + average update<br>• HTMX comment shows without reload |
| Factories   | `factory_boy`                                  | Seed reproducible data                                                                                                 |

---

#### 5.9  Optional enhancements (flag-guarded)

* Vote “likes/dislikes” on comments
* Filter games by platform (API query form)
* i18n (`django-admin makemessages –l es`)
* Advanced test coverage (error paths)
* Favicon & PWA manifest

Implement each behind `settings.ENABLE_<FEATURE>` booleans.

---

### 6. Milestone-based timeline (suggested)

| Week | Deliverable                                      |
| ---- | ------------------------------------------------ |
| 1    | Project bootstrap, core models, admin registered |
| 2    | Import commands, initial data loaded             |
| 3    | Public pages (home, detail) + static styling     |
| 4    | Auth flow & user dashboard                       |
| 5    | HTMX dynamic features                            |
| 6    | Testing suite & optional features                |
| 7    | Code freeze → internal QA                        |

---

### 7. Coding conventions

* **PEP-8** compliant, enforced by `ruff`.
* Use type hints everywhere; run `mypy --strict`.
* Commit messages: “<scope>: <imperative summary>”.
* Keep views thin; business logic in services or model methods.
* No hard-coded URLs – use `reverse()` or `{% url %}`.

---

### 8. Deliverables

1. **Source code** with complete Django project & `requirements.txt`.
2. **README.md** containing:

   * Local setup guide (`python -m venv`, migrations, load sample data)
   * Test execution (`pytest -q`)
   * Optional features & how to toggle them
3. **coverage.xml / HTML** report ≥ 80 % (if unit tests implemented).

---

#### End of document

This plan should give a developer everything needed to start writing code confidently while matching the formal project requirements. Good luck & happy coding!
