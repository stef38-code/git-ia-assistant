# Git IA Assistant

Un ensemble d'outils intelligents pour améliorer votre workflow Git en utilisant des Modèles de Langage (LLM) comme Copilot, Gemini et Ollama.

## 📋 Pré-requis

Avant d'installer l'assistant, assurez-vous de disposer des éléments suivants :

- **Système d'exploitation** : Linux ou macOS.
- **Git** : Installé et configuré sur votre système.
- **Python 3.10+** : Installé avec le module `venv`.
- **Node.js 22+ & npm** : Nécessaires pour les CLI de Copilot et Gemini.
- **Assistants CLI (Recommandé)** :
    - **GitHub Copilot CLI** : [Procédure d'installation](https://github.com/github/gh-copilot) (`npm install -g @github/copilot`).
    - **Gemini CLI** : [Procédure d'installation](https://geminicli.com/) (`npm install -g @google/gemini-cli`).
- **Outils réseau** : `curl` ou `wget` pour l'installation rapide.
- **Clés API** : Selon le moteur IA choisi (Gemini, OpenAI, etc.). Pour Gemini, une clé API [Google AI Studio](https://aistudio.google.com/) est nécessaire.

## 🚀 Vue d'ensemble

Git IA Assistant automatise les tâches répétitives de Git (commits, revues, documentation) et fournit une assistance intelligente pour la qualité du code.

*   **[Fonctionnalités principales](doc/fonctionnalites.md)** : Commits, revues MR/PR, tests, documentation, refactorisation.
*   **[Utilisation du menu `ia`](doc/menu_interactif.md)** : Pilotez tous les outils depuis une interface textuelle riche.

## 📦 Démarrage rapide

### Installation (Linux / macOS)

```bash
curl -fsSL https://raw.githubusercontent.com/stef38-code/git-ia-assistant/master/install.sh | bash
```

Options disponibles :

| Option | Description |
|---|---|
| `-r, --replace` | Supprime l'installation précédente et réinstalle (régénère les scripts d'entrée) |
| `-d, --delete` | Désinstalle complètement l'outil |
| `--dry-run` | Simule l'installation sans modifier le système |
| `-h, --help` | Affiche l'aide |

Pour plus de détails, consultez le **[Guide d'installation complet](doc/installation.md)**.

### Configuration

L'outil nécessite une configuration minimale (Tokens API et choix du moteur IA). Consultez la **[Documentation de configuration](doc/configuration.md)**.

## 🛠️ Utilisation

Lancez simplement la commande `ia` pour accéder au menu interactif :

```bash
ia
```

Pour des exemples détaillés de chaque commande CLI, consultez le **[Guide d'utilisation détaillé](doc/usage.md)**.

## 🧱 Architecture et Développement

Si vous souhaitez contribuer ou comprendre le fonctionnement interne :
*   **[Structure et Architecture](doc/architecture.md)** : Organisation thématique des scripts et prompts.
*   **[Laboratoire et Scénarios futurs](doc/laboratoire.md)**

---

## 📄 Licence
MIT
