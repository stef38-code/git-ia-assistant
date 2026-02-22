#!/usr/bin/env bash

# Script d'installation de git-ia-assistant
# Cible : ${HOME}/.local/share/git-ia-assistant

set -e

REPO_URL="https://github.com/stef38-code/git-ia-assistant.git"
INSTALL_DIR="${HOME}/.local/share/git-ia-assistant"
BIN_DEST="${HOME}/.local/bin"
ALIAS_FILE="${HOME}/.aliases"
TMP_DIR=$(mktemp -d)

# Commandes disponibles
COMMANDS=("git-ia-commit" "git-ia-review" "git-ia-mr" "git-ia-squash" "git-ia-changelog")

function cleanup {
    if [ -d "$TMP_DIR" ]; then
        rm -rf "$TMP_DIR"
    fi
}
trap cleanup EXIT

function check_environment {
    echo "--- Vérification de l'environnement ---"
    if ! command -v git >/dev/null 2>&1; then
        echo "Erreur: 'git' n'est pas installé sur votre système."
        exit 1
    fi

    if ! command -v python3 >/dev/null 2>&1; then
        echo "Erreur: 'python3' n'est pas installé sur votre système."
        exit 1
    fi
}

function fetch_source {
    echo "--- Récupération du code source ---"
    if [ -d ".git" ]; then
        echo "Exécution depuis un dépôt Git local."
        WORKING_DIR="."
    else
        echo "Clonage du dépôt dans un répertoire temporaire..."
        git clone --recursive "$REPO_URL" "$TMP_DIR"
        WORKING_DIR="$TMP_DIR"
    fi
    cd "$WORKING_DIR"
}

function update_submodules {
    echo "--- Mise à jour des sous-modules ---"
    if [ -d ".git" ]; then
        git submodule update --init --recursive
    else
        echo "Attention: .git non trouvé, passage de la mise à jour des sous-modules."
    fi
}

function prepare_venv {
    echo "--- Préparation du répertoire d'installation ---"
    mkdir -p "$INSTALL_DIR"

    if [ ! -d "$INSTALL_DIR/venv" ]; then
        echo "Création de l'environnement virtuel..."
        python3 -m venv "$INSTALL_DIR/venv"
    fi
}

function install_dependencies {
    echo "--- Installation des dépendances ---"
    # Mise à jour de pip
    "$INSTALL_DIR/venv/bin/pip" install --upgrade pip

    # Installation de la librairie commune
    if [ -d "libs/python_commun" ]; then
        echo "Installation de python_commun..."
        "$INSTALL_DIR/venv/bin/pip" install ./libs/python_commun
    else
        echo "Erreur: libs/python_commun non trouvé !"
        exit 1
    fi

    # Installation du projet principal
    echo "Installation de git-ia-assistant..."
    "$INSTALL_DIR/venv/bin/pip" install .
}

function configure_symlinks {
    echo "--- Configuration des liens symboliques ---"
    mkdir -p "$BIN_DEST"

    for cmd in "${COMMANDS[@]}"; do
        echo "Lien symbolique pour $cmd..."
        ln -sf "$INSTALL_DIR/venv/bin/$cmd" "$BIN_DEST/$cmd"
    done
}

function configure_aliases {
    echo "--- Configuration des alias dans $ALIAS_FILE ---"
    
    if [ ! -f "$ALIAS_FILE" ]; then
        echo "Création du fichier $ALIAS_FILE..."
        touch "$ALIAS_FILE"
    fi

    for cmd in "${COMMANDS[@]}"; do
        # Format de l'alias: ia-commit pour git-ia-commit
        alias_name=$(echo "$cmd" | sed 's/git-//')
        alias_cmd="alias $alias_name='$cmd'"
        
        if grep -q "alias $alias_name=" "$ALIAS_FILE"; then
            echo "L'alias '$alias_name' est déjà présent dans $ALIAS_FILE."
        else
            echo "Ajout de l'alias '$alias_name' dans $ALIAS_FILE..."
            echo "$alias_cmd" >> "$ALIAS_FILE"
        fi
    done
}

function main {
    check_environment
    fetch_source
    update_submodules
    prepare_venv
    install_dependencies
    configure_symlinks
    configure_aliases

    echo ""
    echo "Installation terminée avec succès !"
    echo "Les outils sont disponibles dans $BIN_DEST"
    echo "Les alias ont été configurés dans $ALIAS_FILE"
    echo "Assurez-vous que ce répertoire est dans votre PATH et que $ALIAS_FILE est sourcé dans votre .bashrc ou .zshrc."
    echo "Exemple : [ -f ~/.aliases ] && . ~/.aliases"
    echo "Pour vérifier : ia-commit --help"
}

main
