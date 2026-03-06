# Git IA Assistant - Instructions Copilot

## Vue d'ensemble

Git IA Assistant est un outil CLI Python qui intègre plusieurs fournisseurs d'IA (GitHub Copilot, Google Gemini, Ollama) pour améliorer les workflows Git. Il fournit 9 commandes distinctes pour la génération de messages de commit, la revue de code, la documentation, les tests et le refactoring.

## Architecture

### Structure principale

- **`src/git_ia_assistant/cli/`** - Points d'entrée CLI pour chaque commande (`commit_cli.py`, `review_cli.py`, etc.)
- **`src/git_ia_assistant/core/definition/`** - Classes de base abstraites définissant les interfaces pour chaque fonctionnalité
- **`src/git_ia_assistant/ia/{copilot,gemini,ollama}/`** - Implémentations spécifiques à chaque fournisseur
- **`src/git_ia_assistant/prompts/`** - Templates de prompts Markdown utilisés par les fournisseurs d'IA
- **`libs/python_commun/`** - Sous-module Git contenant des utilitaires partagés (logging, opérations Git, détection de langage)

### Pattern Factory

Chaque fonctionnalité utilise un pattern factory pour instancier l'implémentation correcte du fournisseur d'IA :
- `IaAssistantCommitFactory` → retourne `IaCopilotCommit`, `IaGeminiCommit`, ou `IaOllamaCommit`
- `IaAssistantTestFactory` → retourne des générateurs de tests spécifiques au fournisseur
- Pattern similaire pour review, changelog, doc, explain, refacto, squash

Les factories gèrent les imports dynamiques pour éviter les dépendances circulaires.

### Sélection du fournisseur d'IA

Les commandes acceptent le flag `--ia <provider>` ou lisent la variable d'environnement `IA_SELECTED`. Par défaut : `copilot`.

### Système de prompts

Chaque fonctionnalité a un fichier Markdown correspondant dans `src/git_ia_assistant/prompts/` :
- `commit_message_prompt.md` - Messages conformes à Conventional Commits v1.0.0
- `python_review_prompt.md`, `java_review_prompt.md`, `angular_review_prompt.md` - Revues de code spécifiques au langage
- `test_generation_prompt.md` - Supporte PyTest, JUnit, Jest, Vitest, Playwright
- `doc_generation_prompt.md` - Génère des docstrings/Javadoc/KDoc

Les prompts utilisent des placeholders comme `{diff}`, `{langage}`, `{branch_name}` qui sont remplacés par les classes core.

## Configuration de développement

### Configuration initiale
```bash
# Cloner avec le sous-module
git clone --recursive https://github.com/stef38-code/git-ia-assistant.git
cd git-ia-assistant

# Environnement de développement (crée .venv)
chmod +x dev-setup.sh
./dev-setup.sh
source .venv/bin/activate
```

### Installation en production
```bash
# Installe dans ~/.local/share/git-ia-assistant avec des liens symboliques dans ~/.local/bin
./install.sh
```

## Conventions et règles obligatoires

### Scripts avec un main (paramètres CLI)

**Paramètres CLI obligatoires** :
- `-h, --help` : Afficher l'aide (toujours)
```python
if getattr(args, "help", False):
    usage(__file__)  # Affiche la docstring du module
    return
```
- `--dry-run` : Simuler l'installation sans modifier le système (toujours)
- `-r, --replace` : Supprimer et réinstaller (optionnel mais recommandé)
- `-d|--delete` : Suppression de tous les élements relatifs au script

### Priorité d'utilisation des bibliothèques

**Règle principale** :
- ✅ **TOUJOURS** vérifier d'abord si la fonctionnalité existe dans `python_commun`
- ❌ **NE JAMAIS** importer directement `subprocess`, `shutil`, etc. si une fonction existe dans `python_commun`
- 📚 Explorer `libs/python_commun/src/python_commun/` avant d'écrire du code

**Ordre de priorité pour écrire du code** :

1. **python_commun** - TOUJOURS vérifier d'abord
    - Modules : `system`, `logging`, `cli`, `network`, `git`, `vcs`, `ai`
    - Localisation : `libs/python_commun/src/python_commun/`

2. **Bibliothèques tierces** - Si non disponible dans python_commun
    - `requests` pour HTTP
    - `pathlib.Path` pour les chemins

3. **Bibliothèques standard** - En dernier recours uniquement
    - Ne pas importer `subprocess` directement (utiliser `executer_*`)
    - Ne pas importer `shutil` si python_commun a l'équivalent

**Exemple** :
```python
# ❌ MAUVAIS - import direct de subprocess
import subprocess
result = subprocess.run(["sh", "script.sh"], capture_output=True)

# ✅ BON - utilisation de python_commun
from python_commun.system.system import executer_script_shell
result = executer_script_shell("sh script.sh", check=False)
```

### En-têtes de fichiers

Chaque module CLI dispose d'une docstring complète dans le style des pages man Unix :
```python
"""
NAME
    install_<outil> - Description brève

DESCRIPTION
    Description détaillée de ce que fait le script

FUNCTIONS
    nom_fonction(params) -> type_retour
        Description

OPTIONS
    -h, --help      Afficher l'aide
    --dry-run       Simuler le traitement sans modifier le système
    -r, --replace   Supprimer l'installation précédente (optionnel)
"""
```
**Important** : ne pas ajouter la section `FUNCTIONS`, elle ne doit être presente que dans des scripts de type librairie et jamais dans un script par exemple `d'installation` ou `de configuration`

### Parser d'arguments standard

Tous les installateurs doivent utiliser ce pattern pour argparse :
```python
def _parser_options() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Description courte", add_help=False
    )
    parser.add_argument("-h", "--help", action="store_true", help="Afficher l'aide.")
    parser.add_argument("--dry-run", action="store_true", help="Simuler sans rien modifier.")
    parser.add_argument("-r", "--replace", action="store_true", help="Supprimer l'installation précédente.")
    return parser.parse_args()

def main() -> None:
    args = _parser_options()
    if getattr(args, "help", False):
        usage(__file__)  # python_commun.cli.usage
        return
    installer_outil(simulation=args.dry_run, replace=args.replace)
```

### Imports Python

Tous les scripts CLI incluent ces manipulations de chemins pour résoudre les imports :
```python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../libs/python_commun/src")))
```

### Docstrings

Utiliser des docstrings structurées avec les sections : NAME, DESCRIPTION, OPTIONS, FUNCTIONS, DATA.

### Détection de langage

Utiliser `detect_lang_repo()` de `python_commun.system.system` pour identifier le langage du projet (angular, python, java, etc.).

### Format des messages de commit

Lors de la modification du prompt de commit (`commit_message_prompt.md`) :
- Suivre Conventional Commits v1.0.0
- Supporter les scopes basés sur les branches : `feature/XXXX` → `feature(XXXX):`, `hotfix/YYYY` → `hotfix(YYYY):`
- Le body doit être sous forme de liste à puces avec max 3-4 items
- Pas de signatures dans les messages générés
- Messages en français par défaut

### Gestion des versions

**Règle obligatoire** : Mettre à jour la version dans `pyproject.toml` pour chaque modification significative du projet.

#### Versioning sémantique (SemVer)

Format : `MAJOR.MINOR.PATCH` (ex: `0.3.0`)

- **MAJOR** : Changements incompatibles avec les versions précédentes
  - Modification de l'API publique
  - Suppression de commandes CLI
  - Changement de structure de configuration

- **MINOR** : Nouvelles fonctionnalités compatibles
  - Ajout de nouvelles commandes (`git-ia-xxx`)
  - Nouveaux fournisseurs d'IA
  - Nouvelles options CLI
  - Nouveaux prompts

- **PATCH** : Corrections de bugs et améliorations mineures
  - Corrections de bugs
  - Améliorations de prompts existants
  - Optimisations de performance
  - Mises à jour de documentation

#### Quand incrémenter la version

**Toujours incrémenter** pour :
- ✅ Ajout/modification de fonctionnalités
- ✅ Corrections de bugs
- ✅ Modifications des prompts qui changent le comportement
- ✅ Ajout de nouvelles dépendances
- ✅ Changements dans les tests de sécurité

**Pas d'incrémentation** pour :
- ❌ Modifications de README uniquement
- ❌ Ajout de commentaires dans le code
- ❌ Reformatage de code (sans changement de logique)
- ❌ Modifications de `.github/copilot-instructions.md`

#### Mise à jour du fichier

```toml
# pyproject.toml
[project]
name = "git-ia-assistant"
version = "0.3.0"  # ← Modifier ici
```

#### Workflow recommandé

```bash
# 1. Avant de commencer une modification
git checkout -b feature/nouvelle-fonctionnalité

# 2. Développer la fonctionnalité
# ... modifications du code ...

# 3. Incrémenter la version dans pyproject.toml
# 0.3.0 → 0.4.0 (nouvelle fonctionnalité)
# 0.3.0 → 0.3.1 (correction de bug)

# 4. Mettre à jour CHANGELOG.md
echo "## [0.4.0] - $(date +%Y-%m-%d)" >> CHANGELOG.md
echo "### Added" >> CHANGELOG.md
echo "- Description de la fonctionnalité" >> CHANGELOG.md

# 5. Commiter avec git-ia-commit
git add pyproject.toml CHANGELOG.md
git-ia-commit

# 6. Créer un tag après merge sur main
git tag -a v0.4.0 -m "Release version 0.4.0"
git push origin v0.4.0
```

#### Vérification automatique

Créer un pre-commit hook pour vérifier la cohérence :
```bash
# .git/hooks/pre-commit
#!/bin/bash
CURRENT_VERSION=$(grep '^version =' pyproject.toml | cut -d'"' -f2)
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null | sed 's/^v//')

if [ "$CURRENT_VERSION" == "$LAST_TAG" ]; then
    echo "⚠️  La version dans pyproject.toml ($CURRENT_VERSION) n'a pas été incrémentée !"
    echo "   Dernière version : $LAST_TAG"
    echo "   Mettre à jour pyproject.toml avant de commiter."
    exit 1
fi
```

### Points d'entrée CLI

Toutes les commandes sont définies dans `pyproject.toml` sous `[project.scripts]` :
```toml
git-ia-commit = "git_ia_assistant.cli.commit_cli:main"
git-ia-review = "git_ia_assistant.cli.review_cli:main"
# ... etc
```

### Données de package des prompts

Les prompts doivent être inclus dans la distribution du package via `pyproject.toml` :
```toml
[tool.setuptools.package-data]
"git_ia_assistant" = ["prompts/*.md"]
```

## Dépendances

### Requises
- Python ≥ 3.8
- Git
- Dépendances : `google-genai`, `GitPython`, `requests`, `pydantic`, `InquirerPy`, `python-gitlab`, `PyGithub`

### Sous-module
Le sous-module `libs/python_commun` fournit :
- Utilitaires de logging
- Wrappers d'opérations Git
- Détection de langage
- Chargement et formatage de prompts
- Utilitaires système

Toujours mettre à jour le sous-module après un pull : `git submodule update --init --recursive --remote --force libs/python_commun`

## Commandes de test

```bash
# Tester la génération de commit (dry-run affiche le prompt sans appeler l'IA)
git-ia-commit --dry-run

# Tester avec un fournisseur d'IA spécifique
git-ia-commit --ia gemini

# Tester l'optimisation de commits
git-ia-commit --optimise

# Tester les commits partiels
git-ia-commit --optimise --partiel

# Tester la revue de code
git-ia-review
git-ia-review -ia ollama fichier_specifique.py

# Tester la génération de documentation
git-ia-doc mon_code.py

# Tester la génération de tests
git-ia-test composant.py --framework PyTest

# Tester les suggestions de refactoring
git-ia-refacto ancien_script.py --version 3.12
```

## Ajouter de nouvelles fonctionnalités

1. Créer le template de prompt dans `src/git_ia_assistant/prompts/`
2. Créer la classe de base dans `src/git_ia_assistant/core/definition/ia_assistant_<feature>.py`
3. Créer la factory dans `src/git_ia_assistant/core/definition/ia_assistant_<feature>_factory.py`
4. Implémenter les classes spécifiques aux fournisseurs dans `src/git_ia_assistant/ia/{copilot,gemini,ollama}/`
5. Créer le point d'entrée CLI dans `src/git_ia_assistant/cli/<feature>_cli.py`
6. Ajouter l'entrée script dans `pyproject.toml`

## Patterns courants

### Chargement de prompts
```python
from python_commun.ai.prompt import charger_prompt, formatter_prompt

prompt_template = charger_prompt("commit_message_prompt.md")
formatted = formatter_prompt(prompt_template, diff=diff_text, langage=lang, branch_name=branch)
```

### Utilisation de Factory
```python
from git_ia_assistant.core.definition.ia_assistant_commit_factory import IaAssistantCommitFactory

ia_instance = IaAssistantCommitFactory.get_commit_class(ia_choice)
commit_obj = ia_instance(fichiers=files)
message = commit_obj.generer_message()
```

### Mode interactif
Beaucoup de commandes utilisent `InquirerPy` pour les prompts interactifs et les confirmations.

## Règles de sécurité

### Protection des données privées

**RÈGLE ABSOLUE** : Aucune donnée privée ne doit jamais être ajoutée au code source du projet.

#### Données interdites

❌ **JAMAIS** inclure dans le code :
- URLs internes d'entreprise (ex:  `*.company.internal`)
- Codes de projets privés (ex: `AXXX`, codes métiers spécifiques)
- Noms de personnes, usernames, emails d'entreprise
- Tokens/credentials réels (ex: `glpat-xxxxxxxxxxxxxxxxxxxx`)
- Adresses IP privées (`192.168.*`, `10.*`, `172.*`)
- Hostnames de machines internes 
- Chemins absolus spécifiques à un utilisateur 

#### Bonnes pratiques

✅ **TOUJOURS** utiliser :
- URLs génériques pour les exemples : `https://gitlab.com`, `https://github.com`, `https://gitlab.example.com`
- Projets fictifs : `org/repo`, `mygroup/myproject`, `user/repo`
- Tokens masqués : `glpat-xxxxxxxxxxxx`, `$GIT_TOKEN`, `votre_token_ici`
- Chemins relatifs ou variables : `~/`, `$HOME`, variables d'environnement
- Détection automatique au lieu de hardcoding : `"gitlab" in url.lower()` au lieu de lister des URLs

#### Vérification avant commit

Avant chaque commit, scanner le code pour :
```bash
# Rechercher des URLs internes
grep -r "\.server\.\|\.internal\|\.lan" --include="*.py" --include="*.md" .

# Rechercher des tokens réels (patterns glpat-, ghp_)
grep -rE "glpat-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{36,}" --include="*.py" --include="*.md" .

# Rechercher des emails d'entreprise
grep -r "@.*\.fr\|@company\.com" --include="*.py" --include="*.md" .

# Rechercher des IPs privées
grep -r "192\.168\.\|10\.\|172\.(1[6-9]\|2[0-9]\|3[01])\." --include="*.py" --include="*.md" .
```

#### Gestion du sous-module `python_commun`

⚠️ **ATTENTION** : Le sous-module `libs/python_commun` a son propre repository.

Si vous modifiez des fichiers dans `python_commun`, vérifiez également ce repository séparément :
```bash
cd libs/python_commun
git status
# Scanner pour données privées
grep -r "données_privées_pattern" .
```

#### Fichiers à protéger via .gitignore

Le `.gitignore` doit exclure :
- `.env*` - Variables d'environnement et secrets
- `.venv/`, `venv/` - Environnements virtuels Python
- `*.log` - Fichiers de logs
- `__pycache__/`, `*.pyc` - Cache Python
- `build/`, `dist/` - Artefacts de compilation
- `.idea/` - Workspace IDE (peut contenir des chemins absolus)

#### Exemple de code sécurisé

```python
# ❌ MAUVAIS - URL interne hardcodée
if "git-prd.server.lan" in url:
    return GitLabRepository(url)

# ✅ BON - Détection générique
if "gitlab" in url.lower():
    return GitLabRepository(url)

# ❌ MAUVAIS - Token en dur
token = "glpat-xxxxxxxxxxxxxxxxxxxx"

# ✅ BON - Variable d'environnement
token = os.getenv("GIT_TOKEN")
if not token:
    print("Définissez GIT_TOKEN : export GIT_TOKEN='votre_token'")
```

#### Checklist de sécurité

Avant de pousser sur GitHub :
- [ ] Aucune URL interne dans le code
- [ ] Aucun code/nom de projet privé
- [ ] Aucune donnée personnelle (noms, emails)
- [ ] Aucun token/credential réel
- [ ] Aucune IP privée
- [ ] Uniquement des chemins relatifs ou variables
- [ ] Le `.gitignore` protège les fichiers sensibles
- [ ] Le sous-module `python_commun` est aussi vérifié

### Tests de sécurité recommandés

Pour un projet manipulant des tokens et interagissant avec des APIs externes, les tests de sécurité sont **essentiels**.

#### 1. Secrets & Tokens

**Objectif** : Garantir qu'aucun secret n'est exposé dans les logs, le code ou les outputs.

```python
# Tests à implémenter
def test_no_token_in_logs():
    """Vérifie que les tokens ne sont jamais loggués."""
    # Simuler un appel avec token
    # Vérifier que le token est masqué dans les logs

def test_no_hardcoded_secrets():
    """Scanne le code source pour détecter les secrets hardcodés."""
    # Utiliser des patterns regex pour détecter glpat-, ghp_, etc.
    # Échouer si un pattern suspect est trouvé

def test_token_masking_in_output():
    """Vérifie que les credentials sont masqués dans les sorties CLI."""
    # Tester les commandes avec --dry-run
    # Vérifier que les tokens apparaissent comme "***" ou "glpat-xxxx..."
```

**Outils recommandés** :
- `detect-secrets` : Scanner automatique de secrets dans le code
- `truffleHog` : Détection de secrets dans l'historique Git
- Pattern custom : `r"(glpat-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{36,})"`

#### 2. Validation des entrées

**Objectif** : Prévenir les injections et les chemins malveillants.

```python
# Tests à implémenter
def test_path_traversal_prevention():
    """Vérifie que les path traversal sont bloqués."""
    malicious_paths = ["../../etc/passwd", "/etc/shadow", "../.env"]
    # Tester que ces chemins sont rejetés ou normalisés

def test_command_injection_prevention():
    """Vérifie que les commandes shell sont sécurisées."""
    # Tester avec des inputs contenant ; && || ` $ ( )
    # Vérifier qu'aucune injection n'est possible

def test_diff_sanitization():
    """Vérifie que les diffs Git sont sanitizés avant envoi à l'IA."""
    # Créer un diff contenant des caractères spéciaux
    # Vérifier qu'ils sont échappés ou filtrés
```

**Bonnes pratiques** :
- Utiliser `shlex.quote()` pour échapper les arguments shell
- Valider les chemins avec `Path.resolve()` et vérifier qu'ils restent dans le projet
- Limiter la longueur des diffs envoyés aux APIs (prévention de DoS)

#### 3. Scan de dépendances

**Objectif** : Détecter les vulnérabilités dans les dépendances tierces.

```bash
# Commandes à intégrer dans CI/CD
pip install pip-audit safety

# Scanner les vulnérabilités connues
pip-audit --require-hashes --desc
safety check --json

# Analyse statique du code Python
pip install bandit
bandit -r src/ -f json -o bandit-report.json
```

**Configuration GitHub Actions** :
```yaml
# .github/workflows/security.yml
name: Security Scan
on: [push, pull_request]
jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install security tools
        run: |
          pip install pip-audit bandit safety
      - name: Run pip-audit
        run: pip-audit --desc
      - name: Run bandit
        run: bandit -r src/ -ll
      - name: Run safety
        run: safety check
```

#### 4. Sécurité des APIs externes

**Objectif** : Sécuriser les communications avec GitHub, GitLab, Gemini, Ollama.

```python
# Tests à implémenter
def test_https_only():
    """Vérifie que seules les URLs HTTPS sont acceptées."""
    insecure_urls = ["http://api.github.com", "http://gitlab.com"]
    # Vérifier qu'elles sont rejetées ou converties en HTTPS

def test_request_timeout():
    """Vérifie que toutes les requêtes ont un timeout."""
    # Tester que requests.get/post ont timeout=30
    # Prévention de hang indéfini

def test_ssl_verification():
    """Vérifie que la vérification SSL est active."""
    # Tester que verify=True (jamais verify=False)
    # Échouer si SSL est désactivé

def test_rate_limiting():
    """Vérifie que le rate limiting est respecté."""
    # Tester que les requêtes répétées sont throttled
    # Prévention de ban par les APIs
```

**Configuration recommandée** :
```python
# ✅ BON - Configuration sécurisée
import requests

session = requests.Session()
session.verify = True  # Jamais False
session.timeout = 30  # Toujours un timeout

# Vérifier les URLs
if not url.startswith("https://"):
    raise ValueError("HTTPS requis pour les APIs externes")
```

#### 5. Protection des données sensibles

**Objectif** : Minimiser l'exposition des données dans les prompts envoyés aux IAs.

```python
# Tests à implémenter
def test_no_secrets_in_prompts():
    """Vérifie que les secrets ne sont pas envoyés aux APIs d'IA."""
    # Créer un diff contenant un token fictif
    # Vérifier qu'il est filtré avant envoi

def test_diff_size_limit():
    """Vérifie que les diffs sont limités en taille."""
    # Tester avec un diff de 10MB
    # Vérifier qu'il est tronqué ou rejeté

def test_sensitive_file_filtering():
    """Vérifie que les fichiers sensibles sont exclus."""
    sensitive_files = [".env", "secrets.yml", "credentials.json"]
    # Vérifier qu'ils ne sont jamais inclus dans les diffs
```

**Liste de fichiers à exclure** :
```python
SENSITIVE_PATTERNS = [
    r"\.env(\.|$)",
    r".*secret.*",
    r".*credential.*",
    r".*password.*",
    r".*token.*",
    r"id_rsa",
    r"\.pem$",
    r"\.key$",
]
```

#### 6. Checklist des tests de sécurité

Avant chaque release :
- [ ] Aucun secret hardcodé détecté par `detect-secrets`
- [ ] Aucune vulnérabilité critique dans `pip-audit`
- [ ] Score Bandit ≥ B (pas de problème high severity)
- [ ] Tous les appels réseau utilisent HTTPS + timeout
- [ ] Les tokens sont masqués dans tous les outputs
- [ ] Les chemins de fichiers sont validés contre path traversal
- [ ] Les diffs sont sanitizés avant envoi aux APIs d'IA
- [ ] Le `.gitignore` protège tous les fichiers sensibles
- [ ] Les variables d'environnement sont documentées (sans valeurs réelles)

#### 7. Commandes de vérification rapide

```bash
# Scan complet de sécurité
chmod +x scripts/security-check.sh
./scripts/security-check.sh

# Contenu suggéré pour scripts/security-check.sh :
#!/bin/bash
set -e

echo "🔍 Scan des secrets hardcodés..."
detect-secrets scan --baseline .secrets.baseline

echo "🔍 Scan des vulnérabilités de dépendances..."
pip-audit --desc

echo "🔍 Analyse statique de sécurité..."
bandit -r src/ -ll -f screen

echo "🔍 Vérification des patterns dangereux..."
grep -r "verify=False" src/ && echo "❌ SSL verification disabled!" && exit 1
grep -r "http://" src/ --include="*.py" | grep -v "localhost" && echo "❌ HTTP found!" && exit 1

echo "✅ Tous les tests de sécurité sont passés!"
```
