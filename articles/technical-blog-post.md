# Building Cyber With Taptue: A Bilingual Cybersecurity Education Platform with Django

## The Problem

Cybersecurity education has a language problem. The vast majority of free, high-quality resources — TryHackMe rooms, HackTheBox write-ups, blog tutorials, OWASP guides — are in English. For the 500+ million French speakers worldwide, especially in Africa where cybersecurity talent demand is exploding, this creates a barrier that slows careers and leaves critical infrastructure under-protected.

Existing solutions fall short:

- **TryHackMe / HackTheBox** are paid platforms, English-only, with a steep learning curve
- **Cisco NetAcad** costs $200+ per course
- **YouTube security channels** are unstructured with no community
- **OWASP** is reference material, not practical step-by-step guides

**Cyber With Taptue** exists to change that: a free, open-source, bilingual (English/French) cybersecurity education platform built with Django 6.0, PostgreSQL, and HTMX.

---

## The Architecture

### Stack Overview

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.13 + Django 6.0.5 |
| Database | PostgreSQL 16 |
| Frontend | Tailwind CSS 3.4 + HTMX |
| WSGI | Gunicorn |
| Auth | Django auth + django-allauth (Google/GitHub OAuth) |
| Markdown | python-markdown + bleach + Pygments |
| i18n | Django i18n + .po/.mo translations |

### Project Structure

```
cyber_taptue_project/
├── config/                    # Django project configuration
│   ├── settings/
│   │   ├── __init__.py        # Environment switcher (dev/prod)
│   │   ├── base.py            # Shared settings
│   │   ├── development.py     # Dev overrides
│   │   └── production.py      # Prod overrides (HTTPS, HSTS)
│   └── urls.py                # i18n_patterns routing
├── apps/
│   ├── core/                  # Home / About pages
│   ├── accounts/              # CustomUser, Profile, auth views
│   ├── blog/                  # Articles, Categories, Comments, Bookmarks
│   ├── projects/              # Project labs with difficulty levels
│   ├── events/                # Events with photo galleries
│   ├── contact/               # Newsletter subscription
│   ├── meet_legends/          # Podcast/video catalog
│   └── search/                # Full-text search (PostgreSQL SearchVector)
├── locale/fr/                 # French translations (250+ strings)
├── templates/                 # App-organized template hierarchy
├── static/                    # Tailwind CSS source
└── SRS.md                     # 1155-line software requirements spec
```

### Key Design Decisions

#### 1. Bilingual at the Database Level

Instead of separate translation tables (which require expensive JOINs), every content model stores parallel fields with a `_fr` suffix:

```python
class Article(models.Model):
    title = models.CharField(max_length=255)
    title_fr = models.CharField(max_length=255, blank=True)
    content = models.TextField()
    content_fr = models.TextField(blank=True)
    # ...
```

A custom template tag `translated_field` checks the active language and returns the French field if available, falling back to English. This means every content query needs exactly one database call regardless of language — no JOINs, no extra tables, no performance penalty.

#### 2. Server-Rendered Interactivity with HTMX

No JavaScript framework. No React, no Vue, no Alpine. Every interactive element — category filters, pagination, comment posting, newsletter subscription, bookmark toggling — uses HTMX attributes:

```html
<select name="category" 
        hx-get="{% url 'blog:article_list' %}" 
        hx-target="#article-grid">
    {% for cat in categories %}
        <option value="{{ cat.slug }}">{{ cat.name }}</option>
    {% endfor %}
</select>
```

The server returns HTML partials. This keeps the frontend simple, ensures full SEO compatibility (no client-side rendering), and makes the app work with JavaScript disabled for core browsing.

#### 3. Settings Resolution via DJANGO_ENVIRONMENT

Rather than requiring `DJANGO_SETTINGS_MODULE` to point to different files, the `config/settings/__init__.py` reads a single `DJANGO_ENVIRONMENT` variable:

```python
environment = os.environ.get("DJANGO_ENVIRONMENT", "development")
if environment == "production":
    from .production import *
else:
    from .development import *
```

This simplifies deployment — only one environment variable to set across dev, staging, and production.

#### 4. Dual-Backend Full-Text Search

Search uses PostgreSQL's `SearchVector` / `SearchRank` in production for ranked full-text search with proper stemming, and falls back to `icontains` queries for SQLite during development and testing:

```python
if connection.vendor == "postgresql":
    vector = SearchVector("title", "content", "title_fr", "content_fr")
    return Article.objects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.01).order_by("-rank")
else:
    return Article.objects.filter(
        Q(title__icontains=query) | Q(content__icontains=query) |
        Q(title_fr__icontains=query) | Q(content_fr__icontains=query)
    )
```

---

## The 7 Django Apps

### 1. `apps.core` — Static Pages
TemplateView-based home and about pages. No models — the simplest app in the project.

### 2. `apps.accounts` — Custom User & Profiles
- `CustomUser(AbstractUser)` with `email` as `USERNAME_FIELD`
- `Profile` model auto-created via `post_save` signal
- Profile fields: avatar, bio, website, GitHub, LinkedIn, Twitter
- `contribution_count` property sums articles + projects by the user

### 3. `apps.blog` — The Content Engine
- `Article` model with bilingual fields, `PublishedManager`, markdown content
- `Category` model with `name`/`name_fr`, ordered by `order` then `name`
- `Comment` model with threaded replies (self-referential `parent` FK)
- `Bookmark` model for user reading lists (`unique_together` on user + article)
- Nine seeding categories from "Débutant" to "Cloud Security"

### 4. `apps.projects` — Hands-On Labs
- `ProjectLab` model with `difficulty` field (Beginner / Intermediate / Advanced)
- Skills tracking via comma-separated `skills_acquired` field
- GitHub URL and YouTube video support for each lab
- Difficulty filter dropdown on the project list page

### 5. `apps.events` — Event Listings
- `Event` model with start/end dates, venue, patronage
- `photo_gallery` as a JSONField (array of image paths)
- Support for embedded YouTube videos

### 6. `apps.meet_legends` — Podcast & Career Stories
- `Legend` model for cybersecurity professional interviews
- Click-to-play YouTube thumbnail replacement
- Bilingual narrative fields for career stories

### 7. `apps.search` — Full-Text Search
- Searches both `Article` and `ProjectLab` models
- Live HTMX search with partial template updates
- PostgreSQL `SearchVector` on production, `icontains` fallback for dev

---

## Testing Strategy

163 tests across all 7 apps, all passing:

| App | Tests | Coverage |
|-----|-------|----------|
| accounts | 32 | Model, forms, views, profile |
| blog | 96 | Models, views, forms, templatetags, seed, bookmarks, replies, sharing, RSS |
| projects | 20 | Model, views, difficulty filter |
| events | 11 | Model, views |
| contact | 11 | Model, views, newsletter |
| meet_legends | 10 | Model, views |
| search | 13 | Views, HTMX search |

Run with: `python manage.py test apps.accounts.tests apps.blog.tests apps.projects.tests apps.events.tests apps.contact.tests apps.meet_legends.tests apps.search.tests`

---

## Lessons Learned

### What Worked
- **Parallel `_fr` fields** — Bilingual queries are trivially fast (no JOINs). The trade-off is schema duplication, but for a project with < 10 content models, it's the right call.
- **HTMX-first interactivity** — Zero frontend framework complexity. Every interaction returns server-rendered HTML. SEO is automatic. Development velocity is high.
- **Idempotent seed command** — `get_or_create` everywhere. Run it 100 times and get the same result. Critical for CI/CD and developer onboarding.

### What I'd Do Differently
- **Settings discovery** — The `DJANGO_ENVIRONMENT` approach in `__init__.py` is clean, but it took longer to debug than expected because some developers expect `DJANGO_SETTINGS_MODULE` to point directly to the file.
- **JSONField for photo galleries** — Works at current scale, but will need normalization (separate `EventPhoto` model) at scale.
- **Manual `.po` file editing** — Windows developers without `gettext` tools had to compile `.mo` files via `pybabel compile`. In retrospect, a small Docker-based translation workflow would save time.

---

## Roadmap

| Phase | Status | Key Deliverables |
|-------|--------|-----------------|
| **Phase 1: Foundation** | ✅ Complete | Django structure, 7 apps, models, views, templates, HTMX, PostgreSQL, seed, French translations |
| **Phase 2: Quality** | ✅ Complete | 163 tests, user profiles, bookmarks, search, comment replies, RSS, social sharing, difficulty filter |
| **Phase 3: Community** | ✅ Complete | OAuth (Google/GitHub), threaded comments, reading lists |
| **Phase 4: Scale** | 🔜 Next | Docker, CI/CD, email/SendGrid, Redis caching, CDN, analytics |

---

## Contributing

Cyber With Taptue is open source. The full codebase, SRS document, and development setup guide are available. Contributions are welcome — whether it's a new article translation, a bug fix, a project lab, or a feature.

## Try It

```bash
git clone <repo>
python -m venv venv && source venv/bin/activate
pip install -r requirements/development.txt
python manage.py migrate
python manage.py seed_platform
python manage.py runserver
# Visit http://localhost:8000/en/ or http://localhost:8000/fr/
```
