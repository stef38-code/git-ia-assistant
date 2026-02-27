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
