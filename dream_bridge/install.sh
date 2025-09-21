#!/bin/bash
set -e

# -----------------------------
# Détecter l'OS
# -----------------------------
OS_TYPE=$(uname -s)
IS_MAC=false
IS_LINUX=false

if [[ "$OS_TYPE" == "Darwin" ]]; then
    IS_MAC=true
elif [[ "$OS_TYPE" == "Linux" ]]; then
    # Vérifier si c'est WSL
    if grep -qi microsoft /proc/version 2>/dev/null; then
        IS_LINUX=true
    else
        IS_LINUX=true
    fi
else
    echo "OS non supporté : $OS_TYPE"
    exit 1
fi

echo "OS détecté : $OS_TYPE"

# -----------------------------
# Vérifier et installer Python 3.11
# -----------------------------
CURRENT_PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
if [[ $CURRENT_PYTHON_VERSION != 3.11* ]]; then
    echo "Python 3.11 non trouvé (version actuelle : $CURRENT_PYTHON_VERSION). Installation..."
    
    if $IS_LINUX; then
        sudo apt update
        sudo apt install -y software-properties-common
        sudo add-apt-repository -y ppa:deadsnakes/ppa
        sudo apt update
        sudo apt install -y python3.11 python3.11-venv python3.11-dev python3.11-distutils
        sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1
        sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 2
        sudo update-alternatives --config python3
    elif $IS_MAC; then
        # Installer Homebrew si absent
        if ! command -v brew &> /dev/null; then
            echo "Installation de Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            export PATH="/opt/homebrew/bin:$PATH"
        fi
        echo "Installation de Python 3.11 via Homebrew..."
        brew install python@3.11
        brew link --overwrite python@3.11
    fi

    echo "Python 3.11 installé et configuré."
else
    echo "Python 3.11 déjà installé ✔"
fi

# -----------------------------
# Virtualenv
# -----------------------------
if [ ! -d "venv" ]; then
    echo "Création d'un virtualenv..."
    python3 -m venv venv
fi

echo "Activation du virtualenv..."
source venv/bin/activate
pip install --upgrade pip

# -----------------------------
# Installation des packages Python
# -----------------------------
if [ -f "requirements.txt" ]; then
    echo "Installation des packages Python..."
    pip install -r requirements.txt
fi

# -----------------------------
# Redis & Celery
# -----------------------------
if ! command -v redis-server &> /dev/null; then
    echo "Redis non trouvé, installation..."
    if $IS_LINUX; then
        sudo apt update
        sudo apt install -y redis-server
    elif $IS_MAC; then
        brew install redis
    fi
fi

if ! pip show celery &> /dev/null; then
    echo "Celery non trouvé, installation..."
    pip install celery
fi

# Lancement de Redis
echo "Lancement de Redis..."
if $IS_LINUX; then
    redis-server --daemonize yes
elif $IS_MAC; then
    brew services start redis
fi

# Lancement de Celery
echo "Lancement de Celery..."
celery -A dream_bridge worker --loglevel=info &

# -----------------------------
# Migrations Django
# -----------------------------
echo "Application des migrations..."
python3 manage.py migrate

# -----------------------------
# Lancement du serveur Django
# -----------------------------
echo "Lancement du serveur Django..."
python3 manage.py runserver
