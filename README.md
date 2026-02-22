# Git IA Assistant

Un ensemble d'outils intelligents pour améliorer votre workflow Git en utilisant des Modèles de Langage (LLM) comme Copilot, Gemini et Ollama.

## 🚀 Fonctionnalités principales

### Workflow Git standard
*   **Génération de Commits** (`git-ia-commit`) : Analyse vos changements et génère un message conforme à *Conventional Commits*. 
    *   **Mode interactif** : Affinez le message avec des instructions supplémentaires.
    *   **Optimisation** (`--optimise`) : Regroupe intelligemment les fichiers en commits logiques.
    *   **Commits partiels** (`--partiel`) : Découpe un fichier en plusieurs commits via `git add -p`.
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

Chaque outil est disponible sous forme de commande CLI. Par défaut, les outils tentent de détecter l'IA disponible, mais vous pouvez forcer un choix avec l'option `--ia` ou `-ia`.

### 📝 Génération de Commits
Analyse les fichiers modifiés et propose un message de commit.
```bash
git-ia-commit                   # Utilise l'IA par défaut
git-ia-commit --ia gemini       # Force l'utilisation de Gemini
git-ia-commit --dry-run         # Affiche uniquement le diff qui serait envoyé
git-ia-commit --optimise        # Propose des regroupements de commits
git-ia-commit --optimise --partiel # Permet de découper un fichier en plusieurs commits
git-ia-commit -f file1.py       # Analyse uniquement des fichiers spécifiques
```

### 🔍 Revue de Code locale
Analyse vos modifications locales pour suggérer des améliorations.
```bash
git-ia-review                   # Analyse tous les fichiers modifiés
git-ia-review -ia ollama        # Utilise Ollama pour la revue
git-ia-review fichier.py        # Revue d'un fichier spécifique
```

### 🚀 Revue de MR/PR
Réalise une revue complète d'une Merge Request GitLab ou Pull Request GitHub.
```bash
git-ia-mr --url https://github.com/user/repo/pull/123
git-ia-mr -u https://gitlab.com/repo/-/merge_requests/45 -ia gemini
```

### 📚 Documentation
Génère de la documentation pour un fichier source.
```bash
git-ia-doc mon_code.py          # Génère des docstrings Python
git-ia-doc Service.java -f Javadoc -l English
```

### 💡 Explication de Code
Obtenez une explication détaillée d'un fichier complexe.
```bash
git-ia-explain script_complexe.py
```

### 🧪 Génération de Tests
Crée des tests unitaires pour vos fichiers.
```bash
git-ia-test composant.ts --framework Vitest
git-ia-test service.py --type unit
```

### 🛠️ Refactorisation
Propose une version modernisée de votre code.
```bash
git-ia-refacto vieux_script.py --version 3.12
```

### 📜 Changelog & Squash
Gérez votre historique Git.
```bash
git-ia-changelog -c 20          # Génère un changelog sur les 20 derniers commits
git-ia-squash --commits 10      # Suggère des regroupements sur les 10 derniers commits
```

## 🧱 Structure du projet
*   `src/git_ia_assistant/core` : Logique de base et orchestration.
*   `src/git_ia_assistant/ia` : Implémentations spécifiques pour chaque moteur d'IA.
*   `src/git_ia_assistant/prompts` : Templates de prompts Markdown.
*   `libs/python_commun` : (Submodule) Librairie partagée pour les fonctions transverses.

## 📄 Licence
MIT
