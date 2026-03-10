# Git IA Assistant - Instructions de Développement (Gemini CLI)

Ce document définit les standards, l'architecture et les règles obligatoires pour le développement de **Git IA Assistant**. Ces instructions doivent être suivies rigoureusement par l'IA lors de toute intervention sur le codebase.

## 1. Vue d'ensemble du Projet

Git IA Assistant est un outil CLI Python intégrant plusieurs fournisseurs d'IA (GitHub Copilot, Google Gemini, Ollama) pour optimiser les workflows Git (commits, revues de code, documentation, tests, refactoring).

## 2. Architecture et Design Patterns

### Structure des Répertoires
- `src/git_ia_assistant/cli/` : Points d'entrée CLI.
- `src/git_ia_assistant/core/definition/` : Classes de base et interfaces (Abstraites).
- `src/git_ia_assistant/ia/` : Implémentations par fournisseur (copilot, gemini, ollama).
- `src/git_ia_assistant/prompts/` : Templates Markdown pour les prompts.
- `libs/python_commun/` : Sous-module Git pour les utilitaires partagés (Logging, Git, VCS, AI).

### Pattern Factory
Toutes les fonctionnalités utilisent une Factory pour l'instanciation dynamique :
- `IaAssistantCommitFactory` -> `IaCopilotCommit`, `IaGeminiCommit`, etc.
- Les imports doivent être dynamiques dans les factories pour éviter les dépendances circulaires.

## 3. Règles de Codage et Conventions Obligatoires

### Priorité des Bibliothèques (RÈGLE D'OR)
1. **✅ python_commun** : TOUJOURS vérifier si la fonction existe dans `libs/python_commun` avant d'implémenter ou d'importer autre chose.
2. **❌ NE JAMAIS** importer `subprocess`, `shutil` ou `os` pour des opérations système si `python_commun.system` possède un équivalent (ex: `executer_script_shell`).

### Standards CLI (argparse)
Tous les scripts CLI doivent supporter :
- `-h, --help` : Affiche la docstring via `usage(__file__)`.
- `--dry-run` : Simulation sans modification.
- `-r, --replace` : Remplacement d'installation existante.

### En-têtes de Fichiers (Docstrings)
Utiliser le format style "man page" Unix :
- **NAME** : Nom et description brève.
- **DESCRIPTION** : Détails du fonctionnement.
- **OPTIONS** : Liste des drapeaux CLI. Marquer explicitement les options requises avec le tag **(OBLIGATOIRE)** en fin de ligne (ex: `-u, --url URL (OBLIGATOIRE)`).
- **FUNCTIONS / DATA** : (Uniquement pour les bibliothèques).

### Manipulation du `sys.path`
Pour garantir la résolution des imports, insérer les chemins suivants en haut des scripts CLI :
```python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../libs/python_commun/src")))
```

## 4. Gestion des Versions et Commits

### Versioning Sémantique (SemVer)
- Mettre à jour `pyproject.toml` pour chaque changement significatif.
- **MAJOR** : Incompatibilité.
- **MINOR** : Nouvelle fonctionnalité compatible.
- **PATCH** : Correction de bug / optimisation.

### Format des Commits
- Suivre **Conventional Commits v1.0.0**.
- Langue : **Français** par défaut.
- Scope basé sur les branches : `feature/nom` -> `feat(nom):`.
- Body : Liste à puces (max 3-4 points).

### Sous-module `python_commun`
- Toujours mettre à jour le `pyproject.toml` et le `CHANGELOG.md` du sous-module AVANT ceux du projet principal.

## 5. Sécurité et Protection des Données

### Règle Absolue : Zéro Donnée Privée
- **INTERDIT** : URLs internes (`*.lan`, `*.internal`), IPs privées, tokens réels (`glpat-`, `ghp_`), emails nominatifs, codes de projets privés.
- **AUTORISÉ** : Variables d'environnement (`os.getenv`), placeholders (`glpat-xxxx`), URLs génériques (`gitlab.example.com`).

### Validation et Réseau
- Utiliser uniquement **HTTPS**.
- Toujours définir un `timeout` sur les requêtes (ex: `timeout=30`).
- Échapper les arguments shell avec `shlex.quote()`.

## 6. Flux de Travail Gemini CLI

Lorsqu'une tâche est demandée :
1. **Recherche** : Vérifier l'existence d'utilitaires dans `libs/python_commun`.
2. **Implémentation** : Respecter le pattern Factory et les docstrings Unix.
3. **Validation** : S'assurer que les tests de sécurité sont respectés et que la version est incrémentée si nécessaire.
