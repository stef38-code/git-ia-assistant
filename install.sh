#!/usr/bin/env bash

# Script d'installation de git-ia-assistant
# Cible : ${HOME}/.local/share/git-ia-assistant
#
# Usage: install.sh [OPTIONS]
#
# OPTIONS:
#   -h, --help      Afficher cette aide
#   --dry-run       Simuler l'installation sans modifier le système
#   -r, --replace   Supprimer l'installation précédente et réinstaller (régénère les scripts d'entrée)
#   -d, --delete    Supprimer entièrement l'installation

set -e

REPLACE=false
DRY_RUN=false
DELETE=false

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -h|--help)
            sed -n '/^# Usage:/,/^[^#]/{ /^[^#]/d; s/^# \?//; p }' "$0"
            exit 0
            ;;
        --dry-run) DRY_RUN=true ;;
        -r|--replace) REPLACE=true ;;
        -d|--delete) DELETE=true ;;
        *) echo "Option inconnue : $1"; exit 1 ;;
    esac
    shift
done

REPO_URL="https://github.com/stef38-code/git-ia-assistant.git"
INSTALL_DIR="${HOME}/.local/share/git-ia-assistant"
BIN_DEST="${HOME}/.local/bin"
ALIAS_FILE="${HOME}/.aliases"
TMP_DIR=$(mktemp -d)

# Commandes disponibles
COMMANDS=("git-ia-commit" "git-ia-commit-version" "git-ia-commit-v2" "git-ia-review" "git-ia-mr" "git-ia-mr-mcp" "git-ia-squash" "git-ia-changelog" "git-ia-explain" "git-ia-test" "git-ia-doc" "git-ia-refacto" "git-ia-menu")

function cleanup {
    if [ -d "$TMP_DIR" ]; then
        rm -rf "$TMP_DIR"
    fi
}
trap cleanup EXIT

function delete_installation {
    echo "--- Suppression de l'installation existante ---"
    if [ "$DRY_RUN" = true ]; then
        echo "[dry-run] Suppression de $INSTALL_DIR/venv"
        echo "[dry-run] Suppression des liens symboliques dans $BIN_DEST"
        return
    fi
    if [ -d "$INSTALL_DIR/venv" ]; then
        echo "Suppression de l'environnement virtuel : $INSTALL_DIR/venv"
        rm -rf "$INSTALL_DIR/venv"
    fi
    for cmd in "${COMMANDS[@]}"; do
        if [ -L "$BIN_DEST/$cmd" ]; then
            echo "Suppression du lien symbolique $BIN_DEST/$cmd"
            rm -f "$BIN_DEST/$cmd"
        fi
    done
    if [ -L "$BIN_DEST/ia" ]; then
        rm -f "$BIN_DEST/ia"
    fi
    if [ "$DELETE" = true ]; then
        echo "Suppression du répertoire d'installation : $INSTALL_DIR"
        rm -rf "$INSTALL_DIR"
        echo "✅ Désinstallation complète effectuée."
        exit 0
    fi
}
trap cleanup EXIT

function check_environment {
    echo "--- Vérification de l'environnement ---"
    if ! command -v git >/dev/null 2>&1; then
        echo "❌ Erreur: 'git' n'est pas installé. Git est obligatoire pour utiliser cet outil."
        exit 1
    fi

    if ! command -v python3 >/dev/null 2>&1; then
        echo "❌ Erreur: 'python3' est introuvable. Python 3 doit être obligatoirement présent sur votre système."
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
    if [ "$DRY_RUN" = true ]; then
        echo "[dry-run] Création/vérification de $INSTALL_DIR/venv"
        return
    fi
    mkdir -p "$INSTALL_DIR"

    if [ ! -d "$INSTALL_DIR/venv" ]; then
        echo "Création de l'environnement virtuel..."
        python3 -m venv "$INSTALL_DIR/venv"
    fi
}

function install_dependencies {
    echo "--- Installation des dépendances ---"
    if [ "$DRY_RUN" = true ]; then
        echo "[dry-run] pip install --upgrade pip"
        echo "[dry-run] pip install ./libs/python_commun"
        echo "[dry-run] pip install ."
        return
    fi

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

    # Installation du projet principal (force-reinstall pour régénérer les scripts d'entrée)
    echo "Installation de git-ia-assistant..."
    "$INSTALL_DIR/venv/bin/pip" install --force-reinstall .
}

function configure_symlinks {
    echo "--- Configuration des liens symboliques ---"
    if [ "$DRY_RUN" = true ]; then
        for cmd in "${COMMANDS[@]}"; do
            echo "[dry-run] ln -sf $INSTALL_DIR/venv/bin/$cmd $BIN_DEST/$cmd"
        done
        return
    fi
    mkdir -p "$BIN_DEST"

    for cmd in "${COMMANDS[@]}"; do
        echo "Lien symbolique pour $cmd..."
        # Si le binaire n'existe pas dans l'environnement, créer un wrapper qui invoque le script python correspondant
        if [ -x "$INSTALL_DIR/venv/bin/$cmd" ]; then
            ln -sf "$INSTALL_DIR/venv/bin/$cmd" "$BIN_DEST/$cmd"
        else
            # créer un petit wrapper exécutable dans bin dest
            cat > "$BIN_DEST/$cmd" <<EOF
#!/usr/bin/env bash
python3 "$INSTALL_DIR/src/git_ia_assistant/cli/commits/commit_v2.py" "\$@"
EOF
            chmod +x "$BIN_DEST/$cmd"
        fi
    done
}

function configure_aliases {
    echo "--- Configuration des alias dans $ALIAS_FILE ---"
    
    if [ ! -f "$ALIAS_FILE" ]; then
        echo "Création du fichier $ALIAS_FILE..."
        touch "$ALIAS_FILE"
    fi

    for cmd in "${COMMANDS[@]}"; do
        alias_name=${cmd#git-} # Enlever le préfixe git-
        alias_cmd="alias $alias_name='$cmd'" # ex: alias ia-commit='git-ia-commit'
        
        if grep -q "alias $alias_name=" "$ALIAS_FILE"; then
            echo "L'alias '$alias_name' est déjà présent dans $ALIAS_FILE."
        else
            echo "Ajout de l'alias '$alias_name' dans $ALIAS_FILE..."
            echo "$alias_cmd" >> "$ALIAS_FILE"
        fi
    done
}

function create_ia_wrapper {
    echo "--- Configuration du raccourci 'ia' ---"
    
    # Créer le lien symbolique ia -> git-ia-menu (remplacer si existe déjà)
    echo "Création du lien symbolique $BIN_DEST/ia..."
    ln -sf "$INSTALL_DIR/venv/bin/git-ia-menu" "$BIN_DEST/ia"


    # Ajouter l'alias explicite dans .aliases si pas déjà présent
    if [ -f "$ALIAS_FILE" ]; then
        if ! grep -q "alias ia=" "$ALIAS_FILE"; then
            echo "Ajout de l'alias 'ia' dans $ALIAS_FILE..."
            echo "alias ia='git-ia-menu'" >> "$ALIAS_FILE"
        fi
    fi

    echo "✅ Raccourci 'ia' configuré avec succès !"
}

function main {
    check_environment
    if [ "$REPLACE" = true ] || [ "$DELETE" = true ]; then
        delete_installation
    fi
    fetch_source
    update_submodules
    prepare_venv
    install_dependencies
    configure_symlinks
    configure_aliases
    create_ia_wrapper

    echo ""
    echo "Installation terminée avec succès !"
    echo "Les outils sont disponibles dans $BIN_DEST"
    echo "Les alias ont été configurés dans $ALIAS_FILE"
    echo "Le wrapper interactif 'ia' est disponible : utilisez 'ia' pour un menu interactif"
    echo "Assurez-vous que ce répertoire est dans votre PATH et que $ALIAS_FILE est sourcé dans votre .bashrc ou .zshrc."
    echo "Exemple : [ -f ~/.aliases ] && . ~/.aliases"
    echo "Pour vérifier : ia-commit --help ou simplement : ia"
}

main
