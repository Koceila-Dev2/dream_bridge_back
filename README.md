# Dream Bridge - Lancer le projet Django

L’application est également disponible sur notre VPS à cette adresse : *“Insérer le lien”*

---

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
