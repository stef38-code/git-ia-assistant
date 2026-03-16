# Configuration requise

## 🔑 Token d'accès pour les MR/PR (GitLab et GitHub)

La commande `git-ia-mr` nécessite un token d'accès pour récupérer les informations des Merge Requests (GitLab) ou Pull Requests (GitHub).

**⚠️ IMPORTANT - Droits requis selon l'usage** :
- **Sans `--publier`** (revue locale uniquement) : Droits de **lecture seule** suffisent
- **Avec `--publier`** (publication du rapport dans la MR/PR) : Droits d'**écriture** requis

### Créer un Personal Access Token GitLab

1. Connectez-vous sur votre instance GitLab (ex: https://gitlab.com)
2. Allez dans : **User Settings** (icône profil) → **Access Tokens**
3. Créez un nouveau token avec :
   - **Name** : `git-ia-assistant` (ou un nom de votre choix)
   - **Scopes** : 
     - **Pour lecture seule** (sans `--publier`) :
       - ✅ `read_api` (pour lire les informations de la MR)
       - ✅ `read_repository` (pour lire le code source)
     - **Pour lecture + publication** (avec `--publier`) :
       - ✅ `api` (accès complet à l'API - **requis pour publier des commentaires**)
   - **Expiration** : définissez selon vos besoins de sécurité
4. Cliquez sur **Create personal access token**
5. **Copiez le token** (⚠️ il ne sera affiché qu'une seule fois !)

> **💡 Astuce sécurité** : Utilisez deux tokens différents si possible :
> - Token `read_api` pour les revues quotidiennes
> - Token `api` pour la publication automatique (usage ponctuel)

### Créer un Personal Access Token GitHub

#### Option 1 : Classic Token (Simple)

1. Connectez-vous sur https://github.com
2. Allez dans : **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
3. Cliquez sur **Generate new token** → **Generate new token (classic)**
4. Configurez le token :
   - **Note** : `git-ia-assistant`
   - **Scopes** : 
     - **Pour lecture seule** (sans `--publier`) :
       - ✅ `public_repo` (uniquement pour les dépôts publics)
       - ou ✅ `repo` en mode lecture (pour les dépôts privés)
     - **Pour lecture + publication** (avec `--publier`) :
       - ✅ `repo` (accès complet - **requis pour créer des commentaires**)
5. Cliquez sur **Generate token**
6. **Copiez le token** (⚠️ il ne sera plus visible après)

#### Option 2 : Fine-grained Token (Recommandé - Plus sécurisé)

1. Allez dans : **Settings** → **Developer settings** → **Personal access tokens** → **Fine-grained tokens**
2. Cliquez sur **Generate new token**
3. Configurez :
   - **Token name** : `git-ia-assistant`
   - **Repository access** : Sélectionnez les repos spécifiques
   - **Permissions** :
     - **Pour lecture seule** :
       - Contents: `Read-only`
       - Pull requests: `Read-only`
     - **Pour lecture + publication** (avec `--publier`) :
       - Contents: `Read-only`
       - Pull requests: `Read and write` ⚠️ **Requis pour publier**
4. Générez et copiez le token

> **✅ Avantage Fine-grained** : Limite les droits aux repos spécifiques et permet une expiration automatique

### Configurer le token dans votre environnement

Ajoutez cette ligne dans votre `~/.bashrc` ou `~/.zshrc` :
```bash
export GIT_TOKEN='votre_token_ici'
```

Puis rechargez votre configuration :
```bash
source ~/.bashrc  # ou source ~/.zshrc
```

## 🤖 Configuration de l'IA

Par défaut, Git IA Assistant détecte automatiquement l'IA disponible dans cet ordre :
1. **GitHub Copilot** (si `gh copilot` est disponible)
2. **Google Gemini** (si la clé API `GEMINI_API_KEY` est définie)
3. **Ollama** (si le service Ollama est accessible localement)

### Google Gemini
```bash
# Obtenez une clé API sur https://makersuite.google.com/app/apikey
export GEMINI_API_KEY='votre_clé_api_gemini'
```

### Ollama
```bash
# Installez Ollama depuis https://ollama.ai
# Puis lancez un modèle
ollama run llama3
```

## 🔌 Serveurs MCP

### Installation de uv / uvx

`uvx` est nécessaire pour exécuter certains serveurs MCP (comme le serveur `git`). Voici comment l'installer rapidement via `curl` :

```bash
# Installation de uv (inclut uvx)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Vérification et installation des serveurs MCP

Avant d'utiliser les fonctionnalités MCP, vérifiez que tous les serveurs requis sont installés :

```python
from git_ia_assistant.cli.mcp.mcp_config_manager import McpConfigManager

# Vérifie tous les serveurs (affiche les instructions d'installation si manquants)
McpConfigManager.verifier_installation()

# Vérifie uniquement des serveurs spécifiques
McpConfigManager.verifier_installation(["git", "github"])
```

Les serveurs MCP supportés sont :

| Serveur | Package | Lanceur | Commande d'installation |
|---|---|---|---|
| `git` | `mcp-server-git` | `uvx` | `uv pip install mcp-server-git` (ou usage direct via `uvx`) |
| `github` | `@modelcontextprotocol/server-github` | `npx` | `npm install -g @modelcontextprotocol/server-github` |
| `gitlab` | `@modelcontextprotocol/server-gitlab` | `npx` | `npm install -g @modelcontextprotocol/server-gitlab` |
| `sequential-thinking` | `@modelcontextprotocol/server-sequential-thinking` | `npx` | `npm install -g @modelcontextprotocol/server-sequential-thinking` |
| `typescript` | `@modelcontextprotocol/server-typescript` | `npx` | `npm install -g @modelcontextprotocol/server-typescript` |
| `angular` | `@modelcontextprotocol/server-angular` | `npx` | `npm install -g @modelcontextprotocol/server-angular` |
| `filesystem` | `@modelcontextprotocol/server-filesystem` | `npx` | `npm install -g @modelcontextprotocol/server-filesystem` |
| `search` | `@modelcontextprotocol/server-ripgrep` | `npx` | `npm install -g @modelcontextprotocol/server-ripgrep` |
