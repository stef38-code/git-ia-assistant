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
COMMANDS=("git-ia-commit" "git-ia-commit-version" "git-ia-review" "git-ia-mr" "git-ia-squash" "git-ia-changelog" "git-ia-explain" "git-ia-test" "git-ia-doc" "git-ia-refacto")

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

function create_ia_wrapper {
    echo "--- Création du wrapper 'ia' avec fzf ---"
    
    SCRIPTS_DIR="${HOME}/.local/share/scripts"
    IA_SCRIPT="${SCRIPTS_DIR}/ia.sh"
    
    mkdir -p "$SCRIPTS_DIR"
    
    # Créer le script ia.sh avec fzf
    cat > "$IA_SCRIPT" << 'EOFSCRIPT'
#!/usr/bin/env bash
# Wrapper interactif pour git-ia-assistant avec fzf

# Liste des commandes disponibles
COMMANDS=(
    "git-ia-commit"
    "git-ia-commit-version"
    "git-ia-review"
    "git-ia-mr"
    "git-ia-squash"
    "git-ia-changelog"
    "git-ia-explain"
    "git-ia-test"
    "git-ia-doc"
    "git-ia-refacto"
)

# Vérifier si fzf est installé
if ! command -v fzf >/dev/null 2>&1; then
    echo "❌ Erreur: 'fzf' n'est pas installé."
    echo "Installation recommandée:"
    echo "  - Ubuntu/Debian: sudo apt install fzf"
    echo "  - macOS: brew install fzf"
    echo "  - Arch: sudo pacman -S fzf"
    exit 1
fi

# Si un argument est fourni, l'utiliser directement
if [ $# -gt 0 ]; then
    cmd="$1"
    shift
    "$cmd" "$@"
    exit $?
fi

# Sélection interactive avec fzf
selected=$(printf "%s\n" "${COMMANDS[@]}" | fzf \
    --height=60% \
    --border=rounded \
    --prompt="🤖 Sélectionnez une commande IA > " \
    --header="Utilisez ↑/↓ pour naviguer, Enter pour sélectionner, Esc pour annuler" \
    --preview='
        cmd={}
        if command -v "$cmd" >/dev/null 2>&1; then
            "$cmd" --help 2>&1 || echo "Aucune aide disponible pour $cmd"
        else
            echo "❌ Commande '\''$cmd'\'' non trouvée"
            echo ""
            echo "Vérifiez que git-ia-assistant est correctement installé."
            echo "PATH actuel: $PATH"
        fi
    ' \
    --preview-window=right:60%:wrap \
    --color="border:#6272a4,prompt:#50fa7b,pointer:#ff79c6,marker:#f1fa8c,header:#8be9fd")

# Vérifier si une commande a été sélectionnée
if [ -z "$selected" ]; then
    echo "Aucune commande sélectionnée."
    exit 0
fi

# Exécuter la commande sélectionnée
echo "🚀 Exécution de: $selected"
echo ""
"$selected"
EOFSCRIPT

    chmod +x "$IA_SCRIPT"
    
    # Créer le lien symbolique (remplacer si existe déjà)
    echo "Création du lien symbolique $BIN_DEST/ia..."
    ln -sf "$IA_SCRIPT" "$BIN_DEST/ia"
    
    echo "✅ Wrapper 'ia' créé avec succès !"
    echo "   Script: $IA_SCRIPT"
    echo "   Lien: $BIN_DEST/ia"
    
    if ! command -v fzf >/dev/null 2>&1; then
        echo ""
        echo "⚠️  ATTENTION: 'fzf' n'est pas installé sur ce système."
        echo "   Le wrapper 'ia' nécessite fzf pour fonctionner."
        echo "   Installation recommandée:"
        echo "     - Ubuntu/Debian: sudo apt install fzf"
        echo "     - macOS: brew install fzf"
        echo "     - Arch: sudo pacman -S fzf"
    fi
}

function main {
    check_environment
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
