#!/usr/bin/env bash

# Script de configuration de l'environnement de développement pour git-ia-assistant

set -e

echo "--- Mise à jour des sous-modules ---"
if [ -d ".git" ]; then
    git submodule update --init --recursive --remote --force libs/python_commun
else
    echo "Attention : .git non trouvé, passage de la mise à jour des sous-modules."
fi

echo "--- Création de l'environnement virtuel (.venv) ---"
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "Environnement virtuel créé."
else
    echo "L'environnement virtuel existe déjà."
fi

echo "--- Mise à jour de pip ---"
.venv/bin/pip install --upgrade pip

echo "--- Installation de la librairie commune (python_commun) ---"
if [ -d "libs/python_commun" ]; then
    .venv/bin/pip install ./libs/python_commun
else
    echo "Erreur : libs/python_commun non trouvé !"
    exit 1
fi

echo "--- Installation de git-ia-assistant en mode éditable ---"
.venv/bin/pip install -e .

echo ""
echo "Environnement de développement initialisé avec succès !"
echo "Pour l'activer, utilisez la commande suivante :"
echo "source .venv/bin/activate"
echo ""
echo "Vous pouvez maintenant tester les scripts, par exemple :"
echo "git-ia-commit --help"
