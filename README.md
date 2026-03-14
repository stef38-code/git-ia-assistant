# Git IA Assistant

Un ensemble d'outils intelligents pour améliorer votre workflow Git en utilisant des Modèles de Langage (LLM) comme Copilot, Gemini et Ollama. Désormais avec le support **Agentique MCP** pour une précision chirurgicale.

## 📋 Pré-requis

Avant d'installer l'assistant, assurez-vous de disposer des éléments suivants :

- **Système d'exploitation** : Linux ou macOS.
- **Git** : Installé et configuré sur votre système.
- **Python 3.10+** : Installé avec le module `venv`.
- **Node.js 22+ & npm** : Nécessaires pour les CLI de Copilot et Gemini.
- **uv / uvx** : Requis pour le serveur MCP Git (`mcp-server-git`).
    - Installation : `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Assistants CLI (Recommandé)** :
    - **GitHub Copilot CLI** : [Procédure d'installation](https://github.com/github/gh-copilot) (`npm install -g @github/copilot`).
    - **Gemini CLI** : [Procédure d'installation](https://geminicli.com/) (`npm install -g @google/gemini-cli`).
- **Outils réseau** : `curl` ou `wget` pour l'installation rapide.
- **Clés API** : Selon le moteur IA choisi (Gemini, OpenAI, etc.). Pour Gemini, une clé API [Google AI Studio](https://aistudio.google.com/) est nécessaire.

## 🚀 Vue d'ensemble

Git IA Assistant automatise les tâches répétitives de Git (commits, revues, documentation) et fournit une assistance intelligente pour la qualité du code.

*   **[Fonctionnalités principales](doc/fonctionnalites.md)** : Commits, revues MR/PR, tests, documentation, refactorisation.
*   **🚀 Mode Agent (MCP)** : Revue de code autonome où l'IA explore elle-même votre codebase (via `git`, `filesystem`, `ripgrep`).
*   **[Utilisation du menu `ia`](doc/menu_interactif.md)** : Pilotez tous les outils depuis une interface textuelle riche.

## 📦 Démarrage rapide

> Note importante : Lors de la mise à jour du CHANGELOG.md, n'ajouter que les informations nécessaires. Si une information est déjà présente dans le CHANGELOG, ne pas modifier le fichier pour éviter les doublons.


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

### Vérification des serveurs MCP

Avant d'utiliser les fonctionnalités MCP, vérifiez que tous les serveurs requis sont installés :

```python
from git_ia_assistant.cli.mcp.mcp_config_manager import McpConfigManager

# Vérifie tous les serveurs (affiche les instructions d'installation si manquants)
McpConfigManager.verifier_installation()

# Vérifie uniquement des serveurs spécifiques
McpConfigManager.verifier_installation(["git", "github"])
```

Les serveurs MCP supportés sont :

| Serveur | Package | Lanceur |
|---|---|---|
| `git` | `mcp-server-git` | `uvx` |
| `github` | `@modelcontextprotocol/server-github` | `npx` |
| `gitlab` | `@modelcontextprotocol/server-gitlab` | `npx` |
| `sequential-thinking` | `@modelcontextprotocol/server-sequential-thinking` | `npx` |
| `typescript` | `@modelcontextprotocol/server-typescript` | `npx` |
| `angular` | `@modelcontextprotocol/server-angular` | `npx` |
| `sonarqube` | `mcp-server-sonarqube` | `npx` |
| `filesystem` | `@modelcontextprotocol/server-filesystem` | `npx` |
| `search` | `@modelcontextprotocol/server-ripgrep` | `npx` |

## 🤖 Mode Agent (MCP)

La version 1.0.0 introduit le mode **Agent**, accessible via `git-ia-mr-mcp`. Contrairement au mode classique qui envoie tout le diff à l'IA, le mode Agent :
1.  **Configure un environnement sécurisé** avec vos serveurs MCP locaux.
2.  **Fournit des outils** à l'IA (lire un fichier, chercher un texte, voir le diff git).
3.  **Laisse l'IA décider** de ce qu'elle doit explorer pour comprendre votre code.

**Avantage :** Analyse beaucoup plus profonde des impacts, détection des régressions hors-diff et économie massive de tokens.

```bash
# Lancer une revue de MR en mode Agent
ia-mr-mcp -u https://gitlab.com/repo/-/merge_requests/123
```

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
