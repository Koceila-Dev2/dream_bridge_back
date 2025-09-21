📘 README du dépôt
# Dream Bridge – Synthétiseur de rêves

## Description
Dream Bridge est une application web qui transforme vos rêves racontés à voix haute en **images générées par IA**, tout en analysant leur **dimension émotionnelle**.  
Elle permet aussi de suivre l’évolution de son humeur grâce à un **dashboard interactif**.

Projet réalisé dans le cadre du Bachelor Data & IA – HETIC.



## Fonctionnalités
- Authentification et espace personnel
- Enregistrement audio + transcription automatique (Whisper)
- Détection émotionnelle (positif, négatif, neutre)
- Génération d’images via IA (Mistral)
- Dashboard avec filtres (date, émotions, fréquence)
- Phrases du jour personnalisées (Horoscope ou ZenQuotes)
- Gestion des tâches asynchrones (Celery + Redis)

## Stack technique
- **Backend** : Django (Python 3.12)
- **Frontend** : HTML/CSS + Bootstrap + JavaScript
- **BDD** : SQLite (dev) / PostgreSQL (prod)
- **Infra** : VPS OVHcloud (4 vCores / 8Go RAM)
- **APIs** : Whisper, Llama3 (Grok), Gemini, Horoscope API, ZenQuotes
- **Asynchrone** : Celery + Redis


## 1. Cloner le dépôt
- Dépôt : [https://github.com/Koceila-Dev2/dream_bridge_back](https://github.com/Koceila-Dev2/dream_bridge_back)

## 2. Se placer au niveau du fichier `manage.py`
```bash
cd <répertoire_du-projet>


3. Installation manuelle (macOS / Linux / Windows via WSL)

- Créer un environnement virtuel
  - macOS / Linux :
    python3 -m venv venv
    source venv/bin/activate
  - Windows (PowerShell) :
    python -m venv venv
    venv\Scripts\activate

- Installer les dépendances
    pip install --upgrade pip
    pip install -r requirements.txt

- Installer Redis
  - macOS / Linux :
    brew install redis
    brew services start redis
  - Windows via WSL / Ubuntu :
    sudo apt update
    sudo apt install redis-server
    sudo service redis-server start
  > Sur Windows, Redis ne peut pas s’installer nativement. Il faut utiliser WSL / Ubuntu.

- Appliquer les migrations Django
    python manage.py migrate

- Lancer Celery dans un nouveau terminal
    celery -A dream_bridge worker --loglevel=info --pool=solo

- Lancer le serveur de développement
    python manage.py runserver

4. Installation automatique (macOS / Linux / WSL / Ubuntu)

- Le script install.sh installe Python 3.11, l’environnement virtuel, les dépendances et Redis automatiquement.

- Lancer le script
  - macOS / Linux :
    sudo bash install.sh
  - WSL / Ubuntu :
    ./install.sh
  > Sur WSL, assurez-vous d’être dans un terminal Ubuntu, pas PowerShell.

- Lancer le serveur et Celery comme indiqué dans la section précédente
