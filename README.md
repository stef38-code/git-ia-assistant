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

## ⚙️ Configuration requise

### 🔑 Token d'accès pour les MR/PR (GitLab et GitHub)

La commande `git-ia-mr` nécessite un token d'accès pour récupérer les informations des Merge Requests (GitLab) ou Pull Requests (GitHub).

#### Créer un Personal Access Token GitLab

1. Connectez-vous sur votre instance GitLab (ex: https://gitlab.com)
2. Allez dans : **User Settings** (icône profil) → **Access Tokens**
3. Créez un nouveau token avec :
   - **Name** : `git-ia-assistant` (ou un nom de votre choix)
   - **Scopes** : 
     - ✅ `read_api` (pour lire les informations de la MR)
     - ✅ `read_repository` (pour lire le code source)
   - **Expiration** : définissez selon vos besoins de sécurité
4. Cliquez sur **Create personal access token**
5. **Copiez le token** (⚠️ il ne sera affiché qu'une seule fois !)

#### Créer un Personal Access Token GitHub

1. Connectez-vous sur https://github.com
2. Allez dans : **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
3. Cliquez sur **Generate new token** → **Generate new token (classic)**
4. Configurez le token :
   - **Note** : `git-ia-assistant`
   - **Scopes** : 
     - ✅ `repo` (accès complet aux dépôts privés)
     - ou ✅ `public_repo` (uniquement pour les dépôts publics)
5. Cliquez sur **Generate token**
6. **Copiez le token** (⚠️ il ne sera plus visible après)

#### Configurer le token dans votre environnement

**Option A - Pour la session courante uniquement :**
```bash
export GIT_TOKEN='votre_token_ici'
```

**Option B - Configuration permanente (recommandé) :**

Ajoutez cette ligne dans votre `~/.bashrc` ou `~/.zshrc` :
```bash
export GIT_TOKEN='votre_token_ici'
```

Puis rechargez votre configuration :
```bash
source ~/.bashrc  # ou source ~/.zshrc
```

**Option C - Via un fichier .env :**
```bash
# Créez un fichier de configuration
echo "export GIT_TOKEN='votre_token_ici'" > ~/.env-git-ia

# Sourcez-le avant utilisation
source ~/.env-git-ia
```

#### Vérifier la configuration

```bash
# Vérifier que le token est défini
echo $GIT_TOKEN

# Tester avec une MR/PR en mode simulation
git-ia-mr -u https://gitlab.com/org/repo/-/merge_requests/123 --dry-run
```

#### Note de sécurité

⚠️ **Ne partagez jamais votre token** et ne le committez jamais dans Git !  
✅ Ajoutez `*token*` et `.env*` dans votre `.gitignore` si vous stockez des tokens localement.

### 🤖 Configuration de l'IA

Par défaut, Git IA Assistant détecte automatiquement l'IA disponible dans cet ordre :
1. **GitHub Copilot** (si `gh copilot` est disponible)
2. **Google Gemini** (si la clé API `GEMINI_API_KEY` est définie)
3. **Ollama** (si le service Ollama est accessible localement)

Vous pouvez forcer un fournisseur spécifique avec l'option `-ia` ou `--ia` :
```bash
git-ia-commit --ia gemini
git-ia-review -ia ollama
git-ia-mr -u <url> -ia copilot
```

Pour configurer **Gemini** :
```bash
# Obtenez une clé API sur https://makersuite.google.com/app/apikey
export GEMINI_API_KEY='votre_clé_api_gemini'
```

Pour configurer **Ollama** :
```bash
# Installez Ollama depuis https://ollama.ai
# Puis lancez un modèle
ollama run llama3
```

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

**⚠️ Prérequis** : Configurez d'abord la variable `GIT_TOKEN` (voir section Configuration requise ci-dessus)

```bash
# GitLab - Revue d'une Merge Request
git-ia-mr -u https://gitlab.com/org/repo/-/merge_requests/45

# GitHub - Revue d'une Pull Request  
git-ia-mr -u https://github.com/user/repo/pull/123

# Avec un provider IA spécifique
git-ia-mr -u https://gitlab.com/org/repo/-/merge_requests/45 -ia gemini

# Mode simulation (affiche le prompt sans appeler l'IA)
git-ia-mr -u https://gitlab.com/org/repo/-/merge_requests/45 --dry-run

# Afficher l'aide complète
git-ia-mr -h
```

**Sortie** : Le script génère plusieurs fichiers dans `~/ia_assistant/mrOrpr/` :
- `diff_<numero>.patch` : Le diff complet de la MR/PR
- `resume_<numero>.md` : Statistiques et résumé des changements
- `checklist_<numero>.md` : Checklist de revue
- `mrOrpr_<projet>_<numero>.md` : **Rapport final de revue avec analyse IA**

Le rapport final inclut :
- 📊 Analyse générale des changements
- 🔒 Analyse de sécurité (injections, credentials, OWASP)
- 📈 Évaluation de la qualité du code
- ⚠️ Niveau de risque (1-10) avec justification
- ✅ Points bloquants et recommandations

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
