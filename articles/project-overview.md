# Cyber With Taptue: Free, Bilingual Cybersecurity Education for Everyone

Cybersecurity is no longer optional. Every business, government, and individual depends on digital infrastructure that must be defended. Yet the people who need cybersecurity skills most — students in developing countries, career switchers, IT professionals in francophone Africa — face two impossible barriers: **cost** and **language**.

**Cyber With Taptue (CWT)** is our answer. A free, open-source, bilingual (English/French) platform that makes cybersecurity education accessible to anyone with an internet connection.

---

## The Problem We Solve

### The Language Gap
500+ million people speak French worldwide, concentrated in Africa — the fastest-growing continent for tech talent. Yet nearly all free cybersecurity education is in English. Platforms like TryHackMe, HackTheBox, and Cisco NetAcad either charge money or deliver content exclusively in English.

This means a talented IT student in Abidjan, Dakar, or Kinshasa must master English before they can learn to secure networks. That barrier filters out countless future professionals.

### The Cost Barrier
Professional cybersecurity training is expensive:
- Cisco NetAcad: $200+ per course
- CompTIA Security+: $400+ per exam
- SANS training: $5,000+ per course

Even "cheap" options add up fast. Free platforms exist, but they're almost universally English-only and oriented toward entertainment (gamified challenges) rather than structured, production-grade education.

---

## What We Built

### A Complete Learning Platform

Cyber With Taptue is a full-featured educational platform with **7 integrated content types**:

| Feature | What It Offers |
|---------|---------------|
| **📚 Articles** | In-depth tutorials on system hardening, network security, forensics, SIEM, cloud security, and more — all available in English and French |
| **🔬 Project Labs** | Hands-on exercises with difficulty ratings (Beginner / Intermediate / Advanced) so learners progress at their own pace |
| **📅 Events** | Listings for workshops, webinars, and cybersecurity conferences |
| **🎙️ Meet the Legends** | Interviews with cybersecurity professionals — career stories that show learners what's possible |
| **💬 Community** | Threaded comments on every article and project, bookmarking for reading lists |
| **🔍 Search** | Full-text search across all content, in both languages |
| **📧 Newsletter** | Stay updated on new articles, labs, and events |

### Bilingual by Design

Every piece of content on CWT exists in both English and French. Not as an afterthought — it's built into the database schema. When a French speaker visits `/fr/blog/`, they see French titles, French content, and French interface text immediately. Language switching is one click, with no page reload delay.

### Production-Grade Content

We don't teach theory in isolation. Every article is a practical, step-by-step guide tested against real systems. Our flagship article — a comprehensive Debian 12 server hardening guide — runs 9,000+ characters in each language covering SSH hardening, firewall rules, fail2ban, auditd, and kernel parameter tuning.

---

## How It Works (For Users)

### For Learners

1. **Browse** articles by category — from beginner topics like "What is a Firewall?" to advanced cloud security configurations
2. **Filter** project labs by difficulty level — start with Beginner labs and work up to Advanced
3. **Read in your language** — English and French versions of every article, switched instantly
4. **Bookmark** content to build a personal reading list and track your progress
5. **Discuss** — leave comments on articles, reply to others, build knowledge together
6. **Discover careers** — watch interviews with cybersecurity professionals on "Meet the Legends"

### For Contributors

The platform is open source. Writers can submit new articles in either language, translate existing content, add project labs, or fix bugs. The seed command makes local development setup trivial — one command and you have a fully populated local instance.

---

## The Technology Behind It

Built with proven, production-ready technology:
- **Django 6.0** — secure, scalable, batteries-included Python web framework
- **PostgreSQL** — robust relational database with full-text search
- **HTMX** — interactive features without a JavaScript framework (works with JS disabled)
- **Tailwind CSS** — responsive design that works on mobile, tablet, and desktop
- **Google & GitHub OAuth** — sign in with existing accounts
- **163 automated tests** — every feature has test coverage

---

## Current Status

| Metric | Count |
|--------|-------|
| Content categories | 9 (Débutant to Cloud Security) |
| Languages | 2 (English, French) |
| Django apps | 7 |
| Automated tests | 163, all passing |
| French translations | 250+ interface strings, compiled |
| Pages | 22+ (all return 200 in both languages) |

### What's Coming Next

- **Docker deployment** — one-command production setup
- **Email integration** — newsletter delivery via SendGrid
- **CI/CD pipeline** — automated testing and deployment
- **Redis caching** — faster page loads as content grows
- **Content API** — integrate CWT content into other platforms

---

## Who This Is For

- **IT students in francophone Africa** who need cybersecurity skills in their native language
- **Career switchers** moving into cybersecurity from other IT fields
- **Teachers and trainers** looking for free, bilingual course material
- **English-speaking learners** who want a structured, free alternative to paid platforms
- **Cybersecurity professionals** who want to contribute knowledge back to the community

---

## Our Vision

> "Making cybersecurity accessible to everyone — breaking down paywalls, language barriers, and elitism to build the largest free, bilingual cybersecurity knowledge commons."

We believe cybersecurity knowledge should be free. Not "free with a premium tier." Not "free if you already speak English." Truly free — in both language and cost.

Cyber With Taptue is our contribution to that vision. Join us.

---

## Get Involved

- **Read and learn** — visit the platform, browse articles, try a project lab
- **Translate** — help expand French content coverage
- **Write** — contribute articles on topics you know
- **Code** — submit pull requests on GitHub
- **Share** — tell one person about CWT

---

*Cyber With Taptue — Cybersecurity education, free and in your language.*
