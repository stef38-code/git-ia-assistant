# Git IA Assistant

Un ensemble d'outils intelligents pour améliorer votre workflow Git en utilisant des Modèles de Langage (LLM) comme Copilot, Gemini et Ollama.

## 🚀 Fonctionnalités principales

*   **Génération de Commits** (`git-ia-commit`) : Analyse vos changements indexés et génère un message de commit conforme à la spécification *Conventional Commits*.
*   **Revue de Code** (`git-ia-review`) : Analyse vos fichiers locaux modifiés et propose des suggestions d'amélioration (lisibilité, bugs potentiels, bonnes pratiques).
*   **Revue de MR/PR** (`git-ia-mr`) : Automatise la relecture des *Merge Requests* (GitLab) et *Pull Requests* (GitHub) en téléchargeant le diff et en générant un rapport complet.
*   **Stratégie de Squash** (`git-ia-squash`) : Analyse votre historique récent pour suggérer quels commits fusionner lors d'un `git rebase -i`.
*   **Génération de Changelog** (`git-ia-changelog`) : Produit un fichier `CHANGELOG.md` structuré à partir de l'historique des commits.

## 📦 Installation

### 1. Cloner et initialiser
```bash
git clone https://github.com/stef38-code/git-ia-assistant.git
cd git-ia-assistant
git submodule update --init --recursive
```

### 2. Installer en mode éditable
```bash
pip install -e .
```

## 🛠️ Utilisation

Chaque outil est disponible sous forme de commande CLI après l'installation :
*   `git-ia-commit --ia gemini`
*   `git-ia-review --dry-run`
*   `git-ia-mr --url https://github.com/user/repo/pull/1`

## 🧱 Structure du projet
*   `src/git_ia_assistant/core` : Logique de base et orchestration.
*   `src/git_ia_assistant/ia` : Implémentations spécifiques pour chaque moteur d'IA.
*   `src/git_ia_assistant/prompts` : Templates de prompts Markdown.
*   `libs/python_commun` : (Submodule) Librairie partagée pour les fonctions transverses.

## 📄 Licence
MIT
