# Git IA Assistant

Un ensemble d'outils intelligents pour améliorer votre workflow Git en utilisant des Modèles de Langage (LLM) comme Copilot, Gemini et Ollama.

## 🚀 Fonctionnalités principales

### Workflow Git standard
*   **Génération de Commits** (`git-ia-commit`) : Analyse vos changements indexés et génère un message de commit conforme à la spécification *Conventional Commits*. Supporte un **mode interactif** pour affiner le message.
*   **Revue de Code** (`git-ia-review`) : Analyse vos fichiers locaux modifiés et propose des suggestions d'amélioration (lisibilité, bugs potentiels, bonnes pratiques). Supporte l'extraction de contexte pour les imports Python.
*   **Revue de MR/PR** (`git-ia-mr`) : Automatise la relecture des *Merge Requests* (GitLab) et *Pull Requests* (GitHub) en téléchargeant le diff et en générant un rapport complet incluant une **analyse de sécurité** et une **évaluation du risque**.
*   **Stratégie de Squash** (`git-ia-squash`) : Analyse votre historique récent pour suggérer quels commits fusionner lors d'un `git rebase -i`.
*   **Génération de Changelog** (`git-ia-changelog`) : Produit un fichier `CHANGELOG.md` structuré à partir de l'historique des commits.

### Nouveaux outils d'assistance
*   **Explication de Code** (`git-ia-explain`) : Explique de manière pédagogique et structurée un fichier ou une fonction complexe.
*   **Génération de Tests** (`git-ia-test`) : Génère des suites de tests unitaires ou E2E. Supporte **PyTest**, **JUnit 5**, **Jest/Jasmine**, **Vitest** et **Playwright**.
*   **Documentation Automatique** (`git-ia-doc`) : Génère de la documentation technique (Markdown, Javadoc, KDoc, Docstrings Python).
*   **Refactorisation Intelligente** (`git-ia-refacto`) : Propose des améliorations de code (lisibilité, performance, modularité) sans changer le comportement.

## 📦 Installation

### Méthode rapide (curl / wget)

Vous pouvez installer l'assistant directement avec cette commande :

```bash
curl -fsSL https://raw.githubusercontent.com/stef38-code/git-ia-assistant/main/install.sh | bash
```

ou via wget :

```bash
wget -qO- https://raw.githubusercontent.com/stef38-code/git-ia-assistant/main/install.sh | bash
```

### Méthode manuelle

1. Cloner le projet :
```bash
git clone https://github.com/stef38-code/git-ia-assistant.git
cd git-ia-assistant
```

2. Installer :
Utilisez le script d'installation fourni. Il s'occupera de mettre à jour les sous-modules, de créer un environnement virtuel dans `${HOME}/.local/share/git-ia-assistant` et de créer des liens symboliques dans `${HOME}/.local/bin`.

```bash
chmod +x install.sh
./install.sh
```

### Environnement de développement (pour tests et développement)

Si vous souhaitez développer ou tester le projet localement après un `git clone` :

1. Initialiser l'environnement local :
```bash
chmod +x dev-setup.sh
./dev-setup.sh
```

2. Activer l'environnement virtuel :
```bash
source .venv/bin/activate
```

Les commandes (`git-ia-commit`, etc.) seront alors disponibles dans votre terminal tant que l'environnement est actif.

## 🛠️ Utilisation

Chaque outil est disponible sous forme de commande CLI après l'installation (ou via des alias comme `ia-commit`, `ia-test`, etc.) :
*   `git-ia-commit --ia gemini`
*   `git-ia-review --dry-run`
*   `git-ia-mr --url https://github.com/user/repo/pull/1`
*   `git-ia-explain mon_fichier.py`
*   `git-ia-test mon_fichier.java`

## 🧱 Structure du projet
*   `src/git_ia_assistant/core` : Logique de base et orchestration.
*   `src/git_ia_assistant/ia` : Implémentations spécifiques pour chaque moteur d'IA.
*   `src/git_ia_assistant/prompts` : Templates de prompts Markdown.
*   `libs/python_commun` : (Submodule) Librairie partagée pour les fonctions transverses.

## 📄 Licence
MIT
