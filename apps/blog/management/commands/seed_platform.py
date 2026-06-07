"""Seed the platform with realistic cybersecurity content."""
import os
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(BASE))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

import django
django.setup()

from django.utils import timezone
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
from apps.blog.models import Category, Article
from apps.projects.models import ProjectLab
from apps.events.models import Event
from apps.meet_legends.models import Legend

CustomUser = get_user_model()


CATEGORIES = [
    {
        "slug": "cloud-security",
        "name": "Cloud Security",
        "name_fr": "Sécurité Cloud",
        "description": "Cloud security best practices and enterprise hosting hardening guides.",
        "description_fr": "Meilleures pratiques de sécurité cloud et guides de durcissement pour l'hébergement d'entreprise.",
        "order": 1,
        "icon": "☁️",
    },
    {
        "slug": "web-security",
        "name": "Web Security",
        "name_fr": "Sécurité Web",
        "description": "OWASP top 10, secure development, and web application penetration testing.",
        "description_fr": "OWASP top 10, développement sécurisé et tests d'intrusion d'applications web.",
        "order": 2,
        "icon": "🌐",
    },
    {
        "slug": "network-security",
        "name": "Network Security",
        "name_fr": "Sécurité Réseau",
        "description": "Network architecture hardening, monitoring, and intrusion detection.",
        "description_fr": "Durcissement d'architecture réseau, surveillance et détection d'intrusion.",
        "order": 3,
        "icon": "🔒",
    },
    {
        "slug": "osint",
        "name": "OSINT & Threat Intelligence",
        "name_fr": "OSINT & Renseignement sur les Menaces",
        "description": "Open-source intelligence gathering, threat hunting, and digital forensics.",
        "description_fr": "Collecte de renseignements open-source, chasse aux menaces et forensique numérique.",
        "order": 4,
        "icon": "🕵️",
    },
]

def _article_debian_en():
    return r"""# Hardening Debian 12 Bookworm: Step-by-Step Base OS Configuration for Enterprise Hosting

Debian 12 Bookworm is a rock-solid foundation for enterprise hosting, but a default installation leaves numerous attack surfaces exposed. This guide walks through every hardening step — from a minimal ISO boot to a locked-down production configuration.

## Why Debian 12?

Debian's stability, long-term support (five years for Bookworm), and minimal resource footprint make it the distribution of choice for security-conscious hosting environments.

## Prerequisites

- A server or VM with at least 2 GB RAM and 20 GB storage
- The Debian 12 Bookworm netinst ISO
- Root or sudo access during the installation phase

## Step 1: Minimal Base Installation

Boot from the Debian 12 netinst ISO and select **Install** (not Graphical Install) to keep the process lean.

### Partitioning Scheme

| Mount Point | Size     | Filesystem | Description                     |
|-------------|----------|------------|---------------------------------|
| /boot       | 1 GB     | ext4       | Kernel and bootloader           |
| /           | 10–15 GB | ext4       | Root filesystem                 |
| /var        | 5 GB     | ext4       | Variable data (logs, databases) |
| /tmp        | 2 GB     | ext4       | Temporary files (noexec)        |
| swap        | 2 GB     | swap       | Swap partition                  |

### Software Selection

**Deselect all** package groups. A truly minimal system contains only the base utilities.

## Step 2: First Boot and System Update

```bash
apt update && apt upgrade -y && apt full-upgrade -y
apt autoremove --purge -y
```

## Step 3: Network Customization

```bash
apt install openssh-server -y
```

### Secure SSH Configuration

Edit `/etc/ssh/sshd_config`:

```ini
Port 2222
PermitRootLogin no
MaxAuthTries 3
PubkeyAuthentication yes
PasswordAuthentication no
X11Forwarding no
```

## Step 4: Firewall with nftables

```bash
apt install nftables -y
```

Create `/etc/nftables.conf` with a default-deny policy allowing only SSH on port 2222.

## Step 5: Kernel Hardening

Add to `/etc/sysctl.d/99-hardening.conf`:

```ini
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.tcp_syncookies = 1
net.core.somaxconn = 1024
```

## Step 6: Automatic Security Updates

```bash
apt install unattended-upgrades -y
dpkg-reconfigure -plow unattended-upgrades
```

## Step 7: Filesystem Hardening

Add `noexec,nosuid,nodev` to `/tmp` and `/boot` mount options in `/etc/fstab`.

## Step 8: Auditd

```bash
apt install auditd -y
```

## Step 9: fail2ban

```bash
apt install fail2ban -y
```

## Step 10: Verify Hardening

```bash
ss -tlnp
nft list ruleset
sshd -T
auditctl -s
fail2ban-client status sshd
```

## GitHub Repository

Full implementation: https://github.com/russel-taptue/Debian-12-bookworm-server-installation-step-by-step
"""


def _article_debian_fr():
    return r"""# Sécurisation de Debian 12 Bookworm : Guide Étape par Étape

Debian 12 Bookworm constitue une base extrêmement solide pour l'hébergement d'entreprise, mais une installation par défaut expose de nombreuses surfaces d'attaque. Ce guide détaille chaque étape de durcissement.

## Pourquoi Debian 12 ?

La stabilité de Debian, son support à long terme et son empreinte minimale en font la distribution de choix pour les environnements d'hébergement soucieux de la sécurité.

## Prérequis

- Un serveur ou une VM avec au moins 2 Go de RAM et 20 Go de stockage
- L'ISO netinst Debian 12 Bookworm
- Accès root ou sudo

Dépôt GitHub : https://github.com/russel-taptue/Debian-12-bookworm-server-installation-step-by-step
"""


def _article_owasp_en():
    return r"""# OWASP Top 10 2025: A Practical Guide to Web Application Vulnerabilities

The OWASP Top 10 is the industry standard awareness document for web application security. This guide covers each category with exploitation examples and practical mitigations.

## 1. Broken Access Control

Failures in enforcing user permissions allow attackers to access unauthorized functionality.

**Example:** Horizontal privilege escalation by modifying a user ID parameter:
```
GET /api/profile?user_id=123
```
Change to `user_id=124` to access another user's data.

**Mitigation:** Implement server-side access control checks for every request.

## 2. Cryptographic Failures

Weak encryption exposes sensitive data in transit or at rest.

**Example:** Using MD5 for password hashing or TLS 1.0 for HTTPS.

**Mitigation:** Use Argon2id for passwords, enforce TLS 1.2+ with strong ciphers.

## 3. Injection

SQL, NoSQL, OS, and LDAP injection remain prevalent.

```sql
' OR '1'='1' --
```

**Mitigation:** Parameterised queries, input validation, and least privilege database accounts.

## 4. Insecure Design

Security should be baked into the design phase, not bolted on after deployment.

**Mitigation:** Threat modelling, secure design patterns, and regular architecture reviews.

## 5. Security Misconfiguration

Default credentials, verbose error messages, and unnecessary features.

**Mitigation:** Automated configuration scanning, least-functionality principle.

## 6. Vulnerable and Outdated Components

Using libraries with known CVEs.

**Mitigation:** Software Bill of Materials (SBOM), automated dependency scanning.

## 7. Identification and Authentication Failures

Weak password policies, missing MFA, session fixation.

**Mitigation:** Enforce strong passwords, implement MFA, use secure session management.

## 8. Software and Data Integrity Failures

Supply chain attacks, unsigned updates.

**Mitigation:** Code signing, integrity verification, secure CI/CD pipelines.

## 9. Security Logging and Monitoring Failures

Insufficient logging allows attackers to operate undetected.

**Mitigation:** Centralised logging, real-time alerting, immutable log storage.

## 10. Server-Side Request Forgery (SSRF)

Attackers trick the server into making internal network requests.

**Mitigation:** Allow-list outbound destinations, disable unnecessary URL schemas.

## GitHub Repository

Lab environment: https://github.com/russel-taptue/owasp-top-10-2025-lab
"""


def _article_owasp_fr():
    return r"""# OWASP Top 10 2025 : Guide Pratique des Vulnérabilités des Applications Web

L'OWASP Top 10 est le document de référence pour la sécurité des applications web. Ce guide couvre chaque catégorie avec des exemples d'exploitation et des mesures d'atténuation.

1. **Contrôle d'accès défaillant** — Vérifier les permissions côté serveur pour chaque requête.
2. **Défaillances cryptographiques** — Utiliser Argon2id pour les mots de passe, TLS 1.2+.
3. **Injection** — Requêtes paramétrées et validation des entrées.
4. **Conception non sécurisée** — Modélisation des menaces dès la conception.
5. **Mauvaise configuration** — Analyse automatisée de la configuration.
6. **Composants vulnérables** — SBOM et analyse automatisée des dépendances.
7. **Défaillances d'authentification** — Mots de passe forts, MFA.
8. **Défaillances d'intégrité** — Signature de code, pipelines sécurisés.
9. **Journalisation insuffisante** — Journalisation centralisée et alertes en temps réel.
10. **SSRF** — Liste blanche des destinations sortantes.

Dépôt GitHub : https://github.com/russel-taptue/owasp-top-10-2025-lab
"""


def _article_wireshark_en():
    return r"""# Wireshark for Network Forensics: Analyzing Attacks in Packet Captures

Wireshark is the most powerful open-source network protocol analyser. When a breach occurs, packet captures often contain the definitive record of attacker activity.

## Common Attack Patterns to Identify

### ARP Spoofing

Look for duplicate IP addresses with different MAC addresses in rapid succession:

```
arp who-has 192.168.1.1 tell 192.168.1.100
arp is-at 192.168.1.1 aa:bb:cc:dd:ee:ff
```

**Wireshark filter:** `arp.duplicate-address-detected`

### DNS Tunnelling

DNS queries with unusually long subdomains or high query volume to a single domain.

**Wireshark filter:** `dns.qry.name.len > 50`

### TLS Interception

Certificate mismatches or self-signed certificates in corporate traffic.

**Wireshark filter:** `tls.handshake.certificate && !tls.handshake.extensions_server_name`

### Beaconing

Regular, periodic outbound connections to known C2 infrastructure.

**Wireshark filter:** `tcp.flags.syn == 1 and tcp.flags.ack == 0`

Look for connections at fixed intervals (e.g., every 60 seconds).

## Investigation Workflow

1. **Initial triage:** Identify the time window of the incident
2. **Follow TCP streams:** Reconstruct attacker commands
3. **Export objects:** Extract files transferred over HTTP/SMB
4. **Statistical analysis:** IO Graphs, Conversation List, Endpoints
5. **Signature matching:** Apply Suricata rules to the pcap

## Hands-On Exercise

Download the sample pcap from GitHub and identify:
- The initial exploitation vector
- The C2 channel
- The exfiltrated data

## GitHub Repository

https://github.com/russel-taptue/wireshark-forensics-lab
"""


def _article_wireshark_fr():
    return r"""# Wireshark pour la Forensique Réseau : Analyse des Attaques

Wireshark est l'analyseur de protocole réseau open-source le plus puissant. En cas d'intrusion, les captures de paquets contiennent souvent l'enregistrement définitif de l'activité de l'attaquant.

## Techniques d'analyse

- **ARP Spoofing** — Adresses IP dupliquées avec MAC différentes
- **DNS Tunnelling** — Requêtes DNS avec sous-domaines anormalement longs
- **Interception TLS** — Certificats non valides dans le trafic d'entreprise
- **Beaconing** — Connexions sortantes périodiques vers des C2

Dépôt GitHub : https://github.com/russel-taptue/wireshark-forensics-lab
"""


def _article_osint_en():
    return r"""# OSINT Investigation Techniques: From Open Sources to Actionable Intelligence

Open-Source Intelligence (OSINT) is the practice of collecting and analysing publicly available information to produce actionable intelligence. It is used by security researchers, threat hunters, journalists, and law enforcement.

## The OSINT Cycle

1. **Planning** — Define intelligence requirements
2. **Collection** — Gather data from open sources
3. **Processing** — Convert raw data into usable formats
4. **Analysis** — Derive insights and patterns
5. **Dissemination** — Share intelligence with stakeholders

## Key OSINT Domains

### Passive Reconnaissance

- WHOIS lookups (domain registration)
- DNS enumeration (subdomains, MX records, SPF)
- Certificate transparency logs (crt.sh)
- Search engine dorking (Google, Shodan, Censys)

**Example Google dork:**
```
site:example.com filetype:pdf confidential
```

### Social Media Intelligence (SOCMINT)

- Profile correlation across platforms
- Geotagged post analysis
- Network graph analysis (followers, mentions)

### Dark Web Monitoring

- Tor hidden service crawling (ethical limitations apply)
- Telegram channel monitoring
- Pastebin and code repository scraping

### Technical Infrastructure Analysis

- ASN and IP range enumeration
- SSL certificate chain analysis
- Web technology fingerprinting (Wappalyzer, BuiltWith)

## Operational Security for OSINT

- Use isolated browsing environments (Tails, Whonix)
- Rotate VPN endpoints between queries
- Never authenticate to target platforms during passive collection
- Document chain of custody for legal admissibility

## Tools of the Trade

| Tool | Purpose |
|------|---------|
| Maltego | Link analysis and graph mining |
| Recon-ng | Web reconnaissance framework |
| theHarvester | Email and subdomain enumeration |
| SpiderFoot | Automated OSINT aggregation |
| Shodan | Internet-connected device search |

## GitHub Repository

https://github.com/russel-taptue/osint-toolkit
"""


def _article_osint_fr():
    return r"""# Techniques d'Enquête OSINT : Des Sources Ouvertes au Renseignement Actionnable

L'OSINT (Open-Source Intelligence) est la pratique de collecte et d'analyse d'informations publiquement disponibles pour produire du renseignement actionnable.

## Le Cycle OSINT

1. **Planification** — Définir les besoins en renseignement
2. **Collecte** — Rassembler les données
3. **Traitement** — Convertir les données brutes
4. **Analyse** — Dégager des insights
5. **Dissémination** — Partager le renseignement

## Domaines Clés

- **Reconnaissance passive** — WHOIS, DNS, crt.sh, Shodan
- **SOCMINT** — Réseaux sociaux, profils, géolocalisation
- **Dark Web** — Services Tor, Telegram, Pastebin
- **Infrastructure technique** — ASN, SSL, Wappalyzer

Dépôt GitHub : https://github.com/russel-taptue/osint-toolkit
"""


ARTICLES = [
    {
        "slug": "debian-12-bookworm-server-installation",
        "title": "Hardening Debian 12 Bookworm: Step-by-Step Base OS Configuration for Enterprise Hosting",
        "title_fr": "Sécurisation de Debian 12 Bookworm : Guide Étape par Étape de la Configuration de l'OS pour l'Hébergement d'Entreprise",
        "cat_slug": "cloud-security",
        "excerpt": "A complete, production-grade walkthrough for installing and hardening Debian 12 Bookworm from a minimal ISO to a secure enterprise server ready for hosting critical workloads.",
        "excerpt_fr": "Un guide complet et professionnel pour installer et sécuriser Debian 12 Bookworm depuis une ISO minimale jusqu'à un serveur d'entreprise prêt à héberger des charges de travail critiques.",
        "reading_time": 20,
        "github_url": "https://github.com/russel-taptue/Debian-12-bookworm-server-installation-step-by-step",
        "content_en": _article_debian_en(),
        "content_fr": _article_debian_fr(),
    },
    {
        "slug": "owasp-top-10-2025-guide",
        "title": "OWASP Top 10 2025: A Practical Guide to Web Application Vulnerabilities",
        "title_fr": "OWASP Top 10 2025 : Guide Pratique des Vulnérabilités des Applications Web",
        "cat_slug": "web-security",
        "excerpt": "An in-depth walkthrough of the OWASP Top 10 2025 with real-world exploitation examples and mitigation strategies for each vulnerability class.",
        "excerpt_fr": "Un guide approfondi de l'OWASP Top 10 2025 avec des exemples d'exploitation réels et des stratégies d'atténuation pour chaque classe de vulnérabilité.",
        "reading_time": 15,
        "github_url": "https://github.com/russel-taptue/owasp-top-10-2025-lab",
        "content_en": _article_owasp_en(),
        "content_fr": _article_owasp_fr(),
    },
    {
        "slug": "wireshark-network-forensics",
        "title": "Wireshark for Network Forensics: Analyzing Attacks in Packet Captures",
        "title_fr": "Wireshark pour la Forensique Réseau : Analyse des Attaques dans les Captures de Paquets",
        "cat_slug": "network-security",
        "excerpt": "Learn to detect and investigate network intrusions using Wireshark — from ARP spoofing and DNS tunnelling to TLS interception and beaconing analysis.",
        "excerpt_fr": "Apprenez à détecter et enquêter sur les intrusions réseau avec Wireshark — du spoofing ARP au tunneling DNS, en passant par l'interception TLS et l'analyse de balisage.",
        "reading_time": 12,
        "github_url": "https://github.com/russel-taptue/wireshark-forensics-lab",
        "content_en": _article_wireshark_en(),
        "content_fr": _article_wireshark_fr(),
    },
    {
        "slug": "osint-investigation-techniques",
        "title": "OSINT Investigation Techniques: From Open Sources to Actionable Intelligence",
        "title_fr": "Techniques d'Enquête OSINT : Des Sources Ouvertes au Renseignement Actionnable",
        "cat_slug": "osint",
        "excerpt": "A comprehensive guide to OSINT methodology covering passive reconnaissance, social media intelligence, dark web monitoring, and operational security for investigators.",
        "excerpt_fr": "Un guide complet de la méthodologie OSINT couvrant la reconnaissance passive, le renseignement sur les réseaux sociaux, la surveillance du dark web et la sécurité opérationnelle pour les enquêteurs.",
        "reading_time": 10,
        "github_url": "https://github.com/russel-taptue/osint-toolkit",
        "content_en": _article_osint_en(),
        "content_fr": _article_osint_fr(),
    },
]

PROJECTS = [
    {
        "slug": "deploy-hardened-web-server",
        "title": "Deploy a Hardened Web Server with Nginx on Debian 12",
        "title_fr": "Déployer un Serveur Web Durci avec Nginx sur Debian 12",
        "cat_slug": "cloud-security",
        "summary": "Provision a cloud VM, install Nginx with ModSecurity WAF, enforce HTTPS with Let's Encrypt, and harden the entire stack against OWASP Top 10 threats.",
        "summary_fr": "Provisionnez une VM cloud, installez Nginx avec ModSecurity WAF, imposez HTTPS avec Let's Encrypt et durcissez toute la pile contre les menaces OWASP Top 10.",
        "difficulty": "advanced",
        "skills": "Linux, Nginx, ModSecurity, Let's Encrypt, WAF, Bash, System Hardening",
        "skills_fr": "Linux, Nginx, ModSecurity, Let's Encrypt, WAF, Bash, Durcissement Système",
        "github_url": "https://github.com/russel-taptue/hardened-nginx-deploy",
    },
    {
        "slug": "sql-injection-lab",
        "title": "SQL Injection Attack & Defence Lab",
        "title_fr": "Laboratoire d'Attaque et Défense par Injection SQL",
        "cat_slug": "web-security",
        "summary": "Build a deliberately vulnerable web app, exploit SQL injection vulnerabilities manually and with sqlmap, then implement parameterised queries and WAF rules.",
        "summary_fr": "Construisez une application web volontairement vulnérable, exploitez les injections SQL manuellement et avec sqlmap, puis implémentez des requêtes paramétrées et des règles WAF.",
        "difficulty": "intermediate",
        "skills": "SQL, Python, sqlmap, Web Security, Parameterised Queries, Burp Suite",
        "skills_fr": "SQL, Python, sqlmap, Sécurité Web, Requêtes Paramétrées, Burp Suite",
        "github_url": "https://github.com/russel-taptue/sql-injection-lab",
    },
    {
        "slug": "pcap-analysis-challenge",
        "title": "Packet Capture Analysis: Find the Breach",
        "title_fr": "Analyse de Capture Réseau : Trouvez l'Intrusion",
        "cat_slug": "network-security",
        "summary": "Analyse a realistic pcap file containing a multi-stage network intrusion — identify the initial foothold, lateral movement, data exfiltration, and attacker infrastructure.",
        "summary_fr": "Analysez un fichier pcap réaliste contenant une intrusion réseau multi-étapes — identifiez le point d'entrée, le mouvement latéral, l'exfiltration de données et l'infrastructure de l'attaquant.",
        "difficulty": "intermediate",
        "skills": "Wireshark, Network Forensics, PCAP Analysis, Threat Hunting, Zeek, Suricata",
        "skills_fr": "Wireshark, Forensique Réseau, Analyse PCAP, Chasse aux Menaces, Zeek, Suricata",
        "github_url": "https://github.com/russel-taptue/pcap-breach-challenge",
    },
]

EVENTS = [
    {
        "slug": "cybershow-2026",
        "title": "CyberShow 2026: The Future of AI in Cybersecurity",
        "title_fr": "CyberShow 2026 : L'Avenir de l'IA dans la Cybersécurité",
        "venue": "Palais des Congrès, Yaoundé",
        "venue_fr": "Palais des Congrès, Yaoundé",
        "summary": "A two-day conference exploring how artificial intelligence is reshaping cybersecurity — from AI-driven SOC automation to adversarial machine learning.",
        "summary_fr": "Une conférence de deux jours explorant comment l'intelligence artificielle transforme la cybersécurité — de l'automatisation SOC pilotée par l'IA à l'apprentissage automatique adversarial.",
        "start_date": timezone.datetime(2026, 6, 15, 9, 0, tzinfo=timezone.get_current_timezone()),
        "end_date": timezone.datetime(2026, 6, 16, 18, 0, tzinfo=timezone.get_current_timezone()),
        "patronage": "Ministry of Posts and Telecommunications",
        "patronage_fr": "Ministère des Postes et Télécommunications",
        "youtube_video_id": "dQw4w9WgXcQ",
    },
    {
        "slug": "zero-day-workshop-2026",
        "title": "Zero-Day Discovery & Responsible Disclosure Workshop",
        "title_fr": "Atelier de Découverte et Divulgation Responsable de Faille Zero-Day",
        "venue": "Institut Africain d'Informatique, Yaoundé",
        "venue_fr": "Institut Africain d'Informatique, Yaoundé",
        "summary": "Hands-on workshop teaching ethical vulnerability research, fuzzing techniques, and the responsible disclosure process with case studies from real CVEs.",
        "summary_fr": "Atelier pratique enseignant la recherche éthique de vulnérabilités, les techniques de fuzzing et le processus de divulgation responsable avec des études de cas de CVE réels.",
        "start_date": timezone.datetime(2026, 9, 10, 10, 0, tzinfo=timezone.get_current_timezone()),
        "end_date": timezone.datetime(2026, 9, 11, 17, 0, tzinfo=timezone.get_current_timezone()),
        "patronage": "Cameroon Cybersecurity Alliance",
        "patronage_fr": "Alliance Camerounaise de Cybersécurité",
        "youtube_video_id": "dQw4w9WgXcQ",
    },
]

LEGENDS = [
    {
        "slug": "kevin-mitnick",
        "name": "Kevin Mitnick",
        "headline": "From FBI's Most Wanted to the World's Most Celebrated Ethical Hacker",
        "headline_fr": "De l'Homme le Plus Recherché du FBI au Célébre Hackeur Éthique Mondial",
        "narrative": "Kevin Mitnick was once the most wanted computer criminal in the United States. After serving five years in prison, he transformed into a renowned security consultant, author of 'The Art of Deception', and founder of Mitnick Security Consulting. His story remains the ultimate cautionary and inspirational tale in cybersecurity.",
        "narrative_fr": "Kevin Mitnick était autrefois le criminel informatique le plus recherché des États-Unis. Après avoir purgé cinq ans de prison, il est devenu un consultant en sécurité renommé, auteur de 'L'Art de la Supercherie' et fondateur de Mitnick Security Consulting. Son histoire reste le récit à la fois d'avertissement et d'inspiration ultime dans la cybersécurité.",
        "youtube_video_id": "dQw4w9WgXcQ",
    },
    {
        "slug": "eva-galperin",
        "name": "Eva Galperin",
        "headline": "Protecting the Most Vulnerable: Threat Analysis for Human Rights Defenders",
        "headline_fr": "Protéger les Plus Vulnérables : Analyse des Menaces pour les Défenseurs des Droits Humains",
        "narrative": "Eva Galperin is the Director of Cybersecurity at the Electronic Frontier Foundation. She pioneered the 'Stalkerware' classification, built threat intelligence systems for journalists and activists, and co-founded the Coalition Against Stalkerware. Her work focuses on making cybersecurity accessible to those who need it most.",
        "narrative_fr": "Eva Galperin est la Directrice de la Cybersécurité à l'Electronic Frontier Foundation. Elle a pionnié la classification des 'Stalkerwares', construit des systèmes de renseignement sur les menaces pour les journalistes et militants, et co-fondé la Coalition Against Stalkerware. Son travail se concentre sur l'accessibilité de la cybersécurité à ceux qui en ont le plus besoin.",
        "youtube_video_id": "dQw4w9WgXcQ",
    },
    {
        "slug": "mikko-hypponen",
        "name": "Mikko Hyppönen",
        "headline": "Three Decades on the Frontline of Global Malware Research",
        "headline_fr": "Trois Décennies sur la Ligne de Front de la Recherche Mondiale sur les Malwares",
        "narrative": "Mikko Hyppönen has worked at F-Secure since 1991, making him one of the longest-serving security researchers in the industry. He has investigated the most notorious malware outbreaks in history — from Brain and Blaster to Stuxnet and Flame. His TED talks and documentaries have educated millions about the evolving cyber threat landscape.",
        "narrative_fr": "Mikko Hyppönen travaille chez F-Secure depuis 1991, ce qui fait de lui l'un des chercheurs en sécurité les plus anciens de l'industrie. Il a enquêté sur les épidémies de logiciels malveillants les plus notoires de l'histoire — de Brain et Blaster à Stuxnet et Flame. Ses conférences TED et documentaires ont éduqué des millions de personnes sur l'évolution du paysage des menaces informatiques.",
        "youtube_video_id": "dQw4w9WgXcQ",
    },
]


class Command(BaseCommand):
    help = "Seed the platform with realistic cybersecurity content."

    def handle(self, *args, **options):
        self.stdout.write("=== Seeding Cyber With Taptue Platform ===\n")

        founder = self._get_or_create_founder()
        categories = self._seed_categories()
        self._seed_articles(founder, categories)
        self._seed_projects(founder, categories)
        self._seed_events(founder)
        self._seed_legends()

        self.stdout.write(self.style.SUCCESS("\n[v] Platform seeded successfully."))
        self.stdout.write(f"  -> {len(ARTICLES)} articles")
        self.stdout.write(f"  -> {len(PROJECTS)} project labs")
        self.stdout.write(f"  -> {len(EVENTS)} events")
        self.stdout.write(f"  -> {len(LEGENDS)} legends")

    def _get_or_create_founder(self):
        user, created = CustomUser.objects.get_or_create(
            email="taptuerussel@gmail.com",
            defaults={"username": "russel-taptue", "is_staff": True, "is_superuser": True},
        )
        if created:
            user.set_password("FounderSeed2024!")
            user.save()
            self.stdout.write(f"  Created founder user: {user.email}")
        else:
            self.stdout.write(f"  Founder user exists: {user.email}")
        return user

    def _seed_categories(self):
        cats = {}
        for data in CATEGORIES:
            cat_slug = data["slug"]
            cat, created = Category.objects.get_or_create(
                slug=cat_slug,
                defaults={k: v for k, v in data.items() if k != "slug"},
            )
            cats[cat_slug] = cat
            if created:
                self.stdout.write(f"  Created category: {cat.name}")
            else:
                self.stdout.write(f"  Category exists: {cat.name}")
        return cats

    def _seed_articles(self, author, categories):
        for data in ARTICLES:
            slug = data["slug"]
            cat = categories[data["cat_slug"]]
            article, created = Article.objects.get_or_create(
                slug=slug,
                defaults={
                    "title": data["title"],
                    "title_fr": data["title_fr"],
                    "category": cat,
                    "author": author,
                    "content": data["content_en"],
                    "content_fr": data["content_fr"],
                    "excerpt": data["excerpt"],
                    "excerpt_fr": data["excerpt_fr"],
                    "reading_time": data["reading_time"],
                    "is_published": True,
                    "published_at": timezone.now(),
                },
            )
            if created:
                self.stdout.write(f"  Created article: {data['title']}")
            else:
                self.stdout.write(f"  Article exists, skipping: {slug}")

    def _seed_projects(self, author, categories):
        for data in PROJECTS:
            slug = data["slug"]
            cat = categories[data["cat_slug"]]
            project, created = ProjectLab.objects.get_or_create(
                slug=slug,
                defaults={
                    "title": data["title"],
                    "title_fr": data["title_fr"],
                    "category": cat,
                    "author": author,
                    "summary": data["summary"],
                    "summary_fr": data["summary_fr"],
                    "content": f"# {data['title']}\n\n{data['summary']}\n\nFull lab instructions available on GitHub.",
                    "content_fr": f"# {data['title_fr']}\n\n{data['summary_fr']}\n\nInstructions complètes disponibles sur GitHub.",
                    "difficulty": data["difficulty"],
                    "skills_acquired": data["skills"],
                    "skills_acquired_fr": data["skills_fr"],
                    "github_url": data["github_url"],
                    "is_published": True,
                    "published_at": timezone.now(),
                },
            )
            if created:
                self.stdout.write(f"  Created project: {data['title']}")
            else:
                self.stdout.write(f"  Project exists, skipping: {slug}")

    def _seed_events(self, author):
        for data in EVENTS:
            slug = data["slug"]
            event, created = Event.objects.get_or_create(
                slug=slug,
                defaults={
                    "title": data["title"],
                    "title_fr": data["title_fr"],
                    "venue": data["venue"],
                    "venue_fr": data["venue_fr"],
                    "patronage": data["patronage"],
                    "patronage_fr": data["patronage_fr"],
                    "summary": data["summary"],
                    "summary_fr": data["summary_fr"],
                    "content": f"# {data['title']}\n\n{data['summary']}\n\nMore details coming soon.",
                    "content_fr": f"# {data['title_fr']}\n\n{data['summary_fr']}\n\nPlus de détails à venir.",
                    "start_date": data["start_date"],
                    "end_date": data["end_date"],
                    "youtube_video_id": data["youtube_video_id"],
                    "is_published": True,
                    "published_at": timezone.now(),
                },
            )
            if created:
                self.stdout.write(f"  Created event: {data['title']}")
            else:
                self.stdout.write(f"  Event exists, skipping: {slug}")

    def _seed_legends(self):
        for data in LEGENDS:
            slug = data["slug"]
            legend, created = Legend.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": data["name"],
                    "headline": data["headline"],
                    "headline_fr": data["headline_fr"],
                    "narrative": data["narrative"],
                    "narrative_fr": data["narrative_fr"],
                    "youtube_video_id": data["youtube_video_id"],
                    "is_published": True,
                    "published_at": timezone.now(),
                },
            )
            if created:
                self.stdout.write(f"  Created legend: {data['name']}")
            else:
                self.stdout.write(f"  Legend exists, skipping: {slug}")


# ---------------------------------------------------------------------------
# Article content generators (kept as functions to avoid loading at import)
# ---------------------------------------------------------------------------


