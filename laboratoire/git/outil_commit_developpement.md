# Outil de Commit avec Versioning Automatique

## Vue d'ensemble

Ce document décrit un workflow complet de commit intelligent qui s'exécute **en une seule commande** :

```bash
git-ia-commit --version-auto
```

Cette commande unique réalise automatiquement :
1. **Génération de message de commit** avec IA (existant dans `commit_cli.py`)
2. **Détection automatique de la version** actuelle du projet
3. **Incrémentation de version** selon les règles SemVer
4. **Mise à jour du CHANGELOG.md** avec les modifications
5. **Commit des fichiers** (code + version + CHANGELOG)
6. **Push vers le dépôt distant**

## Workflow

```
Développeur → git-ia-commit --version-auto
    ↓
Génération message → Incrémentation version → MAJ CHANGELOG → Commit → Push
```

## Workflow global - Exécution atomique

**IMPORTANT** : Toutes les étapes ci-dessous s'exécutent dans **une seule commande** `git-ia-commit --version-auto`.

```
┌─────────────────────────────────────────────────────────────────────┐
│ COMMANDE UNIQUE : git-ia-commit --version-auto                      │
│                                                                      │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 1. GÉNÉRATION DU MESSAGE DE COMMIT                              │ │
│ │    - Analyse des fichiers modifiés                              │ │
│ │    - Génération du message avec IA (type: feat/fix/chore/...)   │ │
│ │    - Validation par l'utilisateur                               │ │
│ └────────────────────────────────┬────────────────────────────────┘ │
│                                  │                                   │
│                                  ▼                                   │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 2. DÉTECTION DU TYPE DE PROJET                                  │ │
│ │    - Python    → pyproject.toml / setup.py                      │ │
│ │    - Java      → pom.xml / build.gradle                         │ │
│ │    - Node.js   → package.json                                   │ │
│ │    - Go        → go.mod                                          │ │
│ │    - Rust      → Cargo.toml                                      │ │
│ │    - .NET      → *.csproj / *.fsproj                             │ │
│ └────────────────────────────────┬────────────────────────────────┘ │
│                                  │                                   │
│                                  ▼                                   │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 3. EXTRACTION DE LA VERSION ACTUELLE                            │ │
│ │    - Parsing du fichier de configuration                        │ │
│ │    - Détection du numéro de version (format: MAJOR.MINOR.PATCH) │ │
│ │    - Validation du format SemVer                                │ │
│ └────────────────────────────────┬────────────────────────────────┘ │
│                                  │                                   │
│                                  ▼                                   │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 4. ANALYSE DU TYPE DE MODIFICATION (depuis le message)          │ │
│ │    - feat     → MINOR (0.3.0 → 0.4.0)                           │ │
│ │    - fix      → PATCH (0.3.0 → 0.3.1)                           │ │
│ │    - BREAKING  → MAJOR (0.3.0 → 1.0.0)                          │ │
│ │    - chore/docs/style/refactor → PATCH (optionnel selon config) │ │
│ └────────────────────────────────┬────────────────────────────────┘ │
│                                  │                                   │
│                                  ▼                                   │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 5. CALCUL DE LA NOUVELLE VERSION                                │ │
│ │    - Application des règles SemVer                              │ │
│ │    - Confirmation par l'utilisateur                             │ │
│ └────────────────────────────────┬────────────────────────────────┘ │
│                                  │                                   │
│                                  ▼                                   │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 6. MISE À JOUR DU CHANGELOG.md                                  │ │
│ │    - Insertion de la nouvelle section avec la version           │ │
│ │    - Génération automatique depuis le message de commit         │ │
│ │    - Classification par type (Added/Changed/Fixed/Security/...) │ │
│ └────────────────────────────────┬────────────────────────────────┘ │
│                                  │                                   │
│                                  ▼                                   │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 7. MISE À JOUR DU FICHIER DE VERSION                            │ │
│ │    - Python    → pyproject.toml: version = "0.4.0"              │ │
│ │    - Java      → pom.xml: <version>0.4.0</version>              │ │
│ │    - Node.js   → package.json: "version": "0.4.0"               │ │
│ │    - Go        → Utilise les tags Git uniquement                │ │
│ └────────────────────────────────┬────────────────────────────────┘ │
│                                  │                                   │
│                                  ▼                                   │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 8. COMMIT & PUSH                                                │ │
│ │    - Commit : code + version + CHANGELOG                        │ │
│ │    - Push vers le dépôt distant                                 │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

## Étape 1 : Génération du message de commit

### Comportement actuel (commit_cli.py)

Cette étape est **déjà implémentée** dans `src/git_ia_assistant/cli/commit_cli.py` :

```python
# Workflow existant
1. Détection des fichiers modifiés
2. Génération du message avec IA (Copilot/Gemini/Ollama)
3. Format Conventional Commits v1.0.0 :
   - type(scope): description
   - body avec liste à puces
   - footer optionnel (BREAKING CHANGE)
```

### Exemple de message généré

```
feat(git): gestion automatique upstream et détection HEAD détachée

- Détecte automatiquement si la branche n'a pas d'upstream
- Configure avec --set-upstream origin <branch> si nécessaire
- Détecte et bloque le push en cas de HEAD détachée
- Améliore les messages d'erreur pour guider l'utilisateur

BREAKING CHANGE: La fonction pousser_vers_distant() lève maintenant ValueError au lieu de GitCommandError
```

### Types de commits reconnus

| Type       | Impact Version | Description                          |
|------------|----------------|--------------------------------------|
| `feat`     | MINOR          | Nouvelle fonctionnalité              |
| `fix`      | PATCH          | Correction de bug                    |
| `perf`     | PATCH          | Amélioration de performance          |
| `refactor` | PATCH*         | Refactoring sans changement de comportement |
| `style`    | PATCH*         | Formatage, style, whitespace         |
| `docs`     | PATCH*         | Documentation uniquement             |
| `test`     | PATCH*         | Ajout/modification de tests          |
| `build`    | PATCH*         | Build system, dépendances            |
| `ci`       | PATCH*         | Configuration CI/CD                  |
| `chore`    | PATCH*         | Tâches diverses                      |
| `revert`   | PATCH          | Annulation d'un commit précédent     |

\* *Configurable : peut ne pas incrémenter la version selon les préférences du projet*

### Détection de BREAKING CHANGE

Un **MAJOR** (1.0.0) est déclenché si :
- Footer contient `BREAKING CHANGE:` ou `BREAKING-CHANGE:`
- Description contient `!` après le type : `feat!:` ou `fix!:`

## Étape 2 : Détection du type de projet

### Fichiers de configuration par langage

```python
PROJECT_CONFIGS = {
    "python": [
        {
            "file": "pyproject.toml",
            "version_pattern": r'version\s*=\s*"([0-9]+\.[0-9]+\.[0-9]+.*)"',
            "update_template": 'version = "{version}"'
        },
        {
            "file": "setup.py",
            "version_pattern": r'version\s*=\s*["\']([0-9]+\.[0-9]+\.[0-9]+.*)["\']',
            "update_template": 'version="{version}"'
        }
    ],
    "java": [
        {
            "file": "pom.xml",
            "version_pattern": r'<version>([0-9]+\.[0-9]+\.[0-9]+.*)</version>',
            "update_template": '<version>{version}</version>',
            "xml_path": "/project/version"  # XPath pour mise à jour précise
        },
        {
            "file": "build.gradle",
            "version_pattern": r'version\s*[=:]\s*["\']([0-9]+\.[0-9]+\.[0-9]+.*)["\']',
            "update_template": 'version = "{version}"'
        },
        {
            "file": "build.gradle.kts",
            "version_pattern": r'version\s*=\s*"([0-9]+\.[0-9]+\.[0-9]+.*)"',
            "update_template": 'version = "{version}"'
        }
    ],
    "node": [
        {
            "file": "package.json",
            "version_key": "version",  # Utiliser JSON parsing
            "json_mode": True
        }
    ],
    "go": [
        {
            "file": "go.mod",
            "use_git_tags": True,  # Go utilise les tags Git
            "no_file_update": True
        }
    ],
    "rust": [
        {
            "file": "Cargo.toml",
            "version_pattern": r'version\s*=\s*"([0-9]+\.[0-9]+\.[0-9]+.*)"',
            "update_template": 'version = "{version}"'
        }
    ],
    "dotnet": [
        {
            "file": "*.csproj",  # Glob pattern
            "version_pattern": r'<Version>([0-9]+\.[0-9]+\.[0-9]+.*)</Version>',
            "update_template": '<Version>{version}</Version>',
            "xml_path": "/Project/PropertyGroup/Version"
        },
        {
            "file": "*.fsproj",
            "version_pattern": r'<Version>([0-9]+\.[0-9]+\.[0-9]+.*)</Version>',
            "update_template": '<Version>{version}</Version>',
            "xml_path": "/Project/PropertyGroup/Version"
        }
    ]
}
```

### Algorithme de détection

```python
def detecter_type_projet() -> dict:
    """
    Détecte le type de projet et retourne la configuration.
    
    Returns:
        dict: {
            'type': 'python',
            'config_file': 'pyproject.toml',
            'version_pattern': '...',
            'update_template': '...',
            'current_version': '0.3.0'
        }
    """
    racine_git = obtenir_chemin_racine_git()
    
    # Ordre de priorité de détection
    for project_type, configs in PROJECT_CONFIGS.items():
        for config in configs:
            config_path = racine_git / config["file"]
            
            # Support des glob patterns (*.csproj)
            if "*" in config["file"]:
                matches = list(racine_git.glob(config["file"]))
                if matches:
                    config_path = matches[0]
                else:
                    continue
            
            if config_path.exists():
                version = extraire_version(config_path, config)
                if version:
                    return {
                        'type': project_type,
                        'config_file': str(config_path),
                        'config': config,
                        'current_version': version
                    }
    
    # Fallback : utiliser les tags Git
    return {
        'type': 'git-tags',
        'config_file': None,
        'current_version': extraire_version_depuis_tags()
    }
```

## Étape 3 : Extraction de la version actuelle

### Parsing par type de fichier

#### Python (pyproject.toml)
```python
def extraire_version_pyproject(fichier: Path) -> str:
    """Parse pyproject.toml pour extraire la version."""
    import tomli  # ou tomllib en Python 3.11+
    
    with open(fichier, 'rb') as f:
        data = tomli.load(f)
    
    return data.get('project', {}).get('version', None)
```

#### Java (pom.xml)
```python
def extraire_version_pom(fichier: Path) -> str:
    """Parse pom.xml pour extraire la version."""
    import xml.etree.ElementTree as ET
    
    tree = ET.parse(fichier)
    root = tree.getroot()
    
    # Gérer le namespace Maven
    ns = {'mvn': 'http://maven.apache.org/POM/4.0.0'}
    version = root.find('mvn:version', ns)
    
    if version is None:
        version = root.find('version')  # Sans namespace
    
    return version.text if version is not None else None
```

#### Node.js (package.json)
```python
def extraire_version_package_json(fichier: Path) -> str:
    """Parse package.json pour extraire la version."""
    import json
    
    with open(fichier, 'r') as f:
        data = json.load(f)
    
    return data.get('version', None)
```

#### Git Tags (fallback)

```python
def extraire_version_depuis_tags() -> str:
    """Extrait la dernière version depuis les tags Git."""
    import git

    repo = git.Repo('../..')
    tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)

    if not tags:
        return "0.0.0"  # Première version

    derniere_tag = str(tags[-1])
    # Nettoyer le préfixe 'v' si présent
    return derniere_tag.lstrip('v')
```

### Validation du format SemVer

```python
import re

def valider_semver(version: str) -> bool:
    """
    Valide qu'une version respecte le format SemVer.
    
    Formats acceptés :
    - 0.3.0
    - 1.2.3-alpha.1
    - 2.0.0-beta+build.123
    """
    pattern = r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)' \
              r'(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)' \
              r'(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?' \
              r'(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'
    
    return bool(re.match(pattern, version))

def parser_semver(version: str) -> dict:
    """
    Parse une version SemVer.
    
    Returns:
        dict: {
            'major': 0,
            'minor': 3,
            'patch': 0,
            'prerelease': 'alpha.1',
            'build': 'build.123'
        }
    """
    match = re.match(
        r'^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)'
        r'(?:-(?P<prerelease>[0-9A-Za-z\-.]+))?'
        r'(?:\+(?P<build>[0-9A-Za-z\-.]+))?$',
        version
    )
    
    if not match:
        raise ValueError(f"Version invalide : {version}")
    
    return {
        'major': int(match.group('major')),
        'minor': int(match.group('minor')),
        'patch': int(match.group('patch')),
        'prerelease': match.group('prerelease'),
        'build': match.group('build')
    }
```

## Étape 3.5 : Contrôle de la nécessité de changement de version

### Principe

Avant de calculer une nouvelle version, il faut vérifier si la version actuelle a déjà été publiée (c'est-à-dire si un tag Git lui correspond).

- **Tag Git absent** → La version actuelle n'a pas encore été publiée → **Pas de changement de numéro de version** nécessaire.
- **Tag Git présent** → La version a été publiée → **Calcul et proposition d'une nouvelle version**.

### Vérification de l'existence du tag Git

```python
def verifier_tag_git_existe(version: str) -> bool:
    """
    Vérifie si un tag Git correspond à la version donnée.

    Accepte les formats 'v{version}' (ex: v0.3.0) et '{version}' (ex: 0.3.0).

    Args:
        version: Version à vérifier (ex: "0.3.0")

    Returns:
        bool: True si le tag existe, False sinon
    """
    import git

    repo = git.Repo('.')
    tags_existants = [str(tag) for tag in repo.tags]

    return f"v{version}" in tags_existants or version in tags_existants
```

### Détermination de la nécessité d'un changement de version

```python
def determiner_necessite_changement_version(version_actuelle: str) -> bool:
    """
    Détermine si un changement de numéro de version est nécessaire.

    Règle : si le tag Git pour la version actuelle est absent, cela signifie
    que la version courante n'a pas encore été publiée. Dans ce cas, aucun
    changement de numéro de version n'est requis.

    Args:
        version_actuelle: Version courante du projet (ex: "0.3.0")

    Returns:
        bool: True si un changement de version est nécessaire, False sinon
    """
    tag_existe = verifier_tag_git_existe(version_actuelle)

    if not tag_existe:
        logger.log_info(
            f"ℹ️  Le tag v{version_actuelle} n'existe pas dans Git.\n"
            f"   La version {version_actuelle} n'a pas encore été publiée.\n"
            f"   Aucun changement de numéro de version nécessaire."
        )
        return False

    logger.log_info(f"✅ Tag v{version_actuelle} trouvé – calcul de la nouvelle version...")
    return True
```

### Impact sur le workflow

| Situation                         | Comportement                                              |
|-----------------------------------|-----------------------------------------------------------|
| Tag absent (version non publiée)  | Version inchangée, ajout dans la section existante du CHANGELOG |
| Tag présent (version publiée)     | Calcul d'une nouvelle version, nouvelle section dans le CHANGELOG |

## Étape 4 : Analyse du type de modification

### Parsing du message de commit

```python
def analyser_type_commit(message: str) -> dict:
    """
    Analyse un message de commit Conventional Commits.
    
    Returns:
        dict: {
            'type': 'feat',
            'scope': 'git',
            'breaking': False,
            'description': 'gestion automatique upstream',
            'body': '...',
            'footer': '...'
        }
    """
    # Pattern Conventional Commits
    pattern = r'^(?P<type>\w+)(?:\((?P<scope>[^)]+)\))?(?P<breaking>!)?: (?P<description>.+)$'
    
    lignes = message.strip().split('\n')
    premiere_ligne = lignes[0]
    
    match = re.match(pattern, premiere_ligne)
    if not match:
        return {
            'type': 'chore',  # Type par défaut
            'scope': None,
            'breaking': False,
            'description': premiere_ligne
        }
    
    body = '\n'.join(lignes[2:]) if len(lignes) > 2 else ''
    
    # Détection de BREAKING CHANGE dans le footer
    breaking_in_footer = 'BREAKING CHANGE:' in body or 'BREAKING-CHANGE:' in body
    
    return {
        'type': match.group('type'),
        'scope': match.group('scope'),
        'breaking': match.group('breaking') == '!' or breaking_in_footer,
        'description': match.group('description'),
        'body': body
    }
```

### Règles d'incrémentation

```python
def calculer_nouvelle_version(version_actuelle: str, type_commit: dict, config: dict = None) -> str:
    """
    Calcule la nouvelle version selon les règles SemVer.
    
    Args:
        version_actuelle: Version actuelle (ex: "0.3.0")
        type_commit: Résultat de analyser_type_commit()
        config: Configuration optionnelle du projet
        
    Returns:
        str: Nouvelle version (ex: "0.4.0")
    """
    # Configuration par défaut
    config = config or {
        'increment_patch_for': ['fix', 'perf', 'revert'],
        'increment_minor_for': ['feat'],
        'no_increment_for': ['docs', 'style', 'test', 'chore', 'ci', 'build'],
        'respect_breaking_change': True
    }
    
    version = parser_semver(version_actuelle)
    
    # BREAKING CHANGE → MAJOR
    if config['respect_breaking_change'] and type_commit['breaking']:
        version['major'] += 1
        version['minor'] = 0
        version['patch'] = 0
    
    # feat → MINOR
    elif type_commit['type'] in config['increment_minor_for']:
        version['minor'] += 1
        version['patch'] = 0
    
    # fix, perf → PATCH
    elif type_commit['type'] in config['increment_patch_for']:
        version['patch'] += 1
    
    # docs, style, etc. → Pas d'incrémentation
    elif type_commit['type'] in config['no_increment_for']:
        return version_actuelle  # Pas de changement
    
    # Type inconnu → PATCH par défaut
    else:
        version['patch'] += 1
    
    # Reconstruire la version
    nouvelle_version = f"{version['major']}.{version['minor']}.{version['patch']}"
    
    # Conserver prerelease et build si présents
    if version['prerelease']:
        nouvelle_version += f"-{version['prerelease']}"
    if version['build']:
        nouvelle_version += f"+{version['build']}"
    
    return nouvelle_version
```

## Étape 5 : Confirmation utilisateur

### Confirmation du changement de version

La confirmation utilise une saisie texte simple `(y|yes|oui) / (n|no|non)`.
**Un refus ne bloque pas le programme** : le commit se poursuit sans changer la version.

```python
REPONSES_OUI = {"y", "yes", "oui", "o"}
REPONSES_NON = {"n", "no", "non"}


def demander_confirmation(question: str) -> bool:
    """
    Pose une question de confirmation texte (y/n).

    Accepte : y, yes, oui, o  → True
              n, no,  non     → False
    Redemande en cas de saisie invalide.

    Args:
        question: Texte de la question à afficher

    Returns:
        bool: True si l'utilisateur accepte, False sinon
    """
    while True:
        reponse = input(f"{question} [y/n] : ").strip().lower()
        if reponse in REPONSES_OUI:
            return True
        if reponse in REPONSES_NON:
            return False
        print("  ⚠️  Réponse invalide. Entrez 'y' (oui) ou 'n' (non).")


def confirmer_incrementation_version(
    version_actuelle: str,
    nouvelle_version: str,
    type_commit: dict
) -> str | None:
    """
    Demande confirmation à l'utilisateur pour l'incrémentation de version.

    Affiche le résumé et propose :
    - Accepter la version calculée
    - Saisir manuellement une version différente
    - Refuser l'incrémentation (le programme continue sans changer la version)

    Args:
        version_actuelle: Version courante du projet (ex: "0.3.0")
        nouvelle_version: Version calculée (ex: "0.4.0")
        type_commit: Résultat de analyser_type_commit()

    Returns:
        str | None: Nouvelle version acceptée, version saisie manuellement,
                    ou None si l'utilisateur refuse l'incrémentation.
    """
    print(f"\n{'='*60}")
    print(f"📦 Incrémentation de version")
    print(f"{'='*60}")
    print(f"Version actuelle   : {version_actuelle}")
    print(f"Nouvelle version   : {nouvelle_version}")
    print(f"Type de commit     : {type_commit['type']}")
    print(f"Breaking change    : {'Oui ⚠️' if type_commit['breaking'] else 'Non'}")
    print(f"{'='*60}")

    if not demander_confirmation(f"Incrémenter la version ({version_actuelle} → {nouvelle_version}) ?"):
        # Proposer une saisie manuelle avant d'abandonner
        if demander_confirmation("Voulez-vous saisir une version manuellement ?"):
            return saisir_version_manuelle(version_actuelle)
        logger.log_info("ℹ️  Incrémentation refusée – le commit se poursuivra sans changement de version.")
        return None

    return nouvelle_version


def saisir_version_manuelle(version_actuelle: str) -> str:
    """
    Permet à l'utilisateur de saisir manuellement une version SemVer.

    Redemande tant que le format n'est pas valide.

    Args:
        version_actuelle: Version de référence affichée comme exemple

    Returns:
        str: Version valide saisie par l'utilisateur
    """
    while True:
        version = input(
            f"Nouvelle version (actuelle : {version_actuelle}, ex: 1.0.0) : "
        ).strip()

        if valider_semver(version):
            return version

        print(f"  ⚠️  Format invalide '{version}'. Format attendu : MAJOR.MINOR.PATCH (ex: 1.0.0)")
```

## Étape 6 : Mise à jour du CHANGELOG.md

> Règle importante : n'ajouter au CHANGELOG.md que les informations nécessaires. Si une information est déjà présente dans le CHANGELOG, ne pas modifier le fichier pour éviter les doublons.

### Format Keep a Changelog

```markdown
# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
et ce projet adhère à [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2026-03-06

### Added
- Gestion automatique de l'upstream lors du push Git
- Détection de HEAD détachée avant push

### Changed
- Amélioration des messages d'erreur pour guider l'utilisateur

### Security
- Validation stricte de la branche avant push

## [0.3.0] - 2026-03-05

### Added
- Tests unitaires manquants suggérés automatiquement
- Tests de sécurité pour OWASP Top 10
```

### Deux modes de mise à jour du CHANGELOG

| Mode                       | Condition                             | Comportement                                           |
|----------------------------|---------------------------------------|--------------------------------------------------------|
| **Nouvelle section**       | `nouvelle_version != version_actuelle` | Insère une section `## [X.Y.Z]` en haut               |
| **Ajout dans l'existante** | `nouvelle_version == version_actuelle` | Complète la section `## [X.Y.Z]` déjà présente        |

> **Note :** Dans les deux cas, une confirmation `(y|yes|oui)/(n|no|non)` est demandée.  
> Un refus n'interrompt pas le programme – le commit continue sans modifier le CHANGELOG.

### Génération et mise à jour avec confirmation

```python
def proposer_mise_a_jour_changelog(
    fichier_changelog: Path,
    nouvelle_version: str,
    version_actuelle: str,
    type_commit: dict,
    message_commit: str
) -> bool:
    """
    Propose la mise à jour du CHANGELOG.md et demande confirmation.

    Deux comportements selon que la version a changé ou non :
    - Si nouvelle_version != version_actuelle → nouvelle section ## [X.Y.Z]
    - Si nouvelle_version == version_actuelle → ajout dans la section existante

    La confirmation est demandée avant toute écriture.
    Un refus n'interrompt pas le programme.

    Args:
        fichier_changelog: Chemin vers CHANGELOG.md
        nouvelle_version: Version cible (peut être identique à version_actuelle)
        version_actuelle: Version courante du projet
        type_commit: Résultat de analyser_type_commit()
        message_commit: Message de commit complet

    Returns:
        bool: True si le changelog a été mis à jour, False sinon
    """
    entree_generee = _generer_entree_changelog(nouvelle_version, type_commit)

    print(f"\n{'='*60}")
    print(f"📋 Mise à jour proposée pour CHANGELOG.md")
    print(f"{'='*60}")

    if nouvelle_version != version_actuelle:
        print(f"Mode        : Nouvelle section ## [{nouvelle_version}]")
    else:
        print(f"Mode        : Ajout dans la section existante ## [{version_actuelle}]")

    print(f"\nContenu à ajouter :\n{'-'*40}")
    print(entree_generee.strip())
    print(f"{'='*60}")

    if not demander_confirmation("Mettre à jour le CHANGELOG.md ?"):
        logger.log_info("ℹ️  Mise à jour du CHANGELOG refusée – le commit continue sans modification.")
        return False

    if nouvelle_version != version_actuelle:
        mettre_a_jour_changelog_nouvelle_section(fichier_changelog, nouvelle_version, entree_generee)
    else:
        mettre_a_jour_changelog_section_existante(fichier_changelog, version_actuelle, entree_generee)

    logger.log_info(f"✅ CHANGELOG.md mis à jour (version {nouvelle_version})")
    return True


def _generer_entree_changelog(version: str, type_commit: dict) -> str:
    """
    Génère le bloc de texte à insérer dans le CHANGELOG.

    Args:
        version: Version cible
        type_commit: Résultat de analyser_type_commit()

    Returns:
        str: Bloc Markdown prêt à l'insertion
    """
    from datetime import date

    MAPPING_CATEGORIES = {
        'feat': 'Added',
        'fix': 'Fixed',
        'perf': 'Changed',
        'refactor': 'Changed',
        'style': 'Changed',
        'docs': 'Documentation',
        'test': 'Testing',
        'build': 'Build',
        'ci': 'CI/CD',
        'chore': 'Maintenance',
        'revert': 'Removed',
        'security': 'Security',
    }

    categorie = 'Security' if type_commit['breaking'] else MAPPING_CATEGORIES.get(type_commit['type'], 'Changed')

    body_lines = type_commit.get('body', '').strip().split('\n')
    points = [
        ligne.strip('- ').strip()
        for ligne in body_lines
        if ligne.strip().startswith('-')
    ]

    if not points:
        points = [type_commit['description']]

    entree = f"### {categorie}\n"
    for point in points:
        entree += f"- {point}\n"

    return entree


def mettre_a_jour_changelog_nouvelle_section(
    fichier_changelog: Path,
    nouvelle_version: str,
    contenu_section: str
) -> None:
    """
    Insère une nouvelle section ## [X.Y.Z] - YYYY-MM-DD en tête du changelog.

    Args:
        fichier_changelog: Chemin vers CHANGELOG.md
        nouvelle_version: Version de la nouvelle section
        contenu_section: Corps Markdown de la section (### Added, etc.)
    """
    import re
    from datetime import date

    entete_section = f"## [{nouvelle_version}] - {date.today()}\n\n"
    nouvelle_entree = entete_section + contenu_section + "\n"

    if not fichier_changelog.exists():
        contenu = (
            "# Changelog\n\n"
            "Toutes les modifications notables de ce projet seront documentées dans ce fichier.\n\n"
            "Le format est basé sur [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),\n"
            "et ce projet adhère à [Semantic Versioning](https://semver.org/spec/v2.0.0.html).\n\n"
            + nouvelle_entree
        )
    else:
        with open(fichier_changelog, 'r', encoding='utf-8') as fichier:
            contenu = fichier.read()

        # Insérer après le préambule (avant la première section ##)
        pattern = r'(# Changelog.*?adhère à.*?\n\n)'
        correspondance = re.search(pattern, contenu, re.DOTALL)

        if correspondance:
            position = correspondance.end()
            contenu = contenu[:position] + nouvelle_entree + contenu[position:]
        else:
            contenu = nouvelle_entree + contenu

    with open(fichier_changelog, 'w', encoding='utf-8') as fichier:
        fichier.write(contenu)


def mettre_a_jour_changelog_section_existante(
    fichier_changelog: Path,
    version_actuelle: str,
    contenu_a_ajouter: str
) -> None:
    """
    Ajoute du contenu dans la section ## [version_actuelle] déjà présente.

    Si la section n'existe pas encore, crée une nouvelle section.

    Args:
        fichier_changelog: Chemin vers CHANGELOG.md
        version_actuelle: Version dont la section sera complétée
        contenu_a_ajouter: Corps Markdown à insérer (### Added, etc.)
    """
    import re

    if not fichier_changelog.exists():
        # Pas de changelog → créer avec une section neuve
        mettre_a_jour_changelog_nouvelle_section(fichier_changelog, version_actuelle, contenu_a_ajouter)
        return

    with open(fichier_changelog, 'r', encoding='utf-8') as fichier:
        contenu = fichier.read()

    # Chercher la section de la version actuelle
    pattern_section = rf'(## \[{re.escape(version_actuelle)}\][^\n]*\n)'
    correspondance = re.search(pattern_section, contenu)

    if not correspondance:
        # Section absente → créer une nouvelle section
        logger.log_info(
            f"ℹ️  Section [{version_actuelle}] absente du CHANGELOG – création d'une nouvelle section."
        )
        mettre_a_jour_changelog_nouvelle_section(fichier_changelog, version_actuelle, contenu_a_ajouter)
        return

    # Insérer le contenu juste après le titre de la section
    position_insertion = correspondance.end()
    contenu = contenu[:position_insertion] + "\n" + contenu_a_ajouter + contenu[position_insertion:]

    with open(fichier_changelog, 'w', encoding='utf-8') as fichier:
        fichier.write(contenu)
```

### Gestion des catégories multiples

```python
def categoriser_changements(message_commit: str) -> dict:
    """
    Catégorise les changements d'un commit en plusieurs sections.
    
    Utile pour les commits qui touchent plusieurs aspects.
    
    Returns:
        dict: {
            'Added': ['Feature X', 'Feature Y'],
            'Changed': ['Amélioration Z'],
            'Fixed': [],
            'Security': []
        }
    """
    categories = {
        'Added': [],
        'Changed': [],
        'Fixed': [],
        'Deprecated': [],
        'Removed': [],
        'Security': []
    }
    
    # Mots-clés pour détection automatique
    keywords = {
        'Added': ['ajoute', 'ajout', 'nouveau', 'nouvelle', 'introduit'],
        'Changed': ['modifie', 'améliore', 'optimise', 'refactor'],
        'Fixed': ['corrige', 'correction', 'fix', 'résout', 'répare'],
        'Security': ['sécurité', 'vulnérabilité', 'CVE', 'authentification'],
        'Deprecated': ['déprécié', 'obsolète', 'deprecated'],
        'Removed': ['supprime', 'retire', 'enlève']
    }
    
    # Parser le body du commit
    lignes = message_commit.split('\n')
    for ligne in lignes:
        ligne = ligne.strip('- ').strip().lower()
        if not ligne:
            continue
        
        # Détecter la catégorie
        for categorie, mots_cles in keywords.items():
            if any(mot in ligne for mot in mots_cles):
                categories[categorie].append(ligne)
                break
        else:
            # Par défaut : Changed
            categories['Changed'].append(ligne)
    
    # Nettoyer les catégories vides
    return {k: v for k, v in categories.items() if v}
```

## Étape 7 : Mise à jour du fichier de version

### Python (pyproject.toml)

```python
def mettre_a_jour_pyproject_toml(fichier: Path, nouvelle_version: str) -> None:
    """Met à jour la version dans pyproject.toml."""
    import tomli
    import tomli_w  # pip install tomli-w
    
    with open(fichier, 'rb') as f:
        data = tomli.load(f)
    
    data['project']['version'] = nouvelle_version
    
    with open(fichier, 'wb') as f:
        tomli_w.dump(data, f)
    
    logger.log_info(f"pyproject.toml mis à jour : {nouvelle_version}")
```

### Java (pom.xml)

```python
def mettre_a_jour_pom_xml(fichier: Path, nouvelle_version: str) -> None:
    """Met à jour la version dans pom.xml."""
    import xml.etree.ElementTree as ET
    
    # Parser avec préservation de la structure
    tree = ET.parse(fichier)
    root = tree.getroot()
    
    # Gérer le namespace Maven
    ns = {'mvn': 'http://maven.apache.org/POM/4.0.0'}
    
    # Trouver l'élément <version>
    version_elem = root.find('mvn:version', ns)
    if version_elem is None:
        version_elem = root.find('version')  # Sans namespace
    
    if version_elem is not None:
        version_elem.text = nouvelle_version
        
        # Sauvegarder avec indentation
        ET.indent(tree, space='  ')
        tree.write(fichier, encoding='utf-8', xml_declaration=True)
        
        logger.log_info(f"pom.xml mis à jour : {nouvelle_version}")
    else:
        logger.log_warn("Impossible de trouver <version> dans pom.xml")
```

#### Alternative : Maven Versions Plugin

```python
def mettre_a_jour_pom_avec_maven(nouvelle_version: str) -> None:
    """Utilise le plugin Maven pour mettre à jour la version."""
    from python_commun.system.system import executer_commande_shell
    
    cmd = f"mvn versions:set -DnewVersion={nouvelle_version} -DgenerateBackupPoms=false"
    resultat = executer_commande_shell(cmd, check=True)
    
    if resultat.returncode == 0:
        logger.log_info(f"pom.xml mis à jour via Maven : {nouvelle_version}")
    else:
        logger.log_error("Échec de la mise à jour du pom.xml")
        raise RuntimeError("Échec Maven versions:set")
```

### Node.js (package.json)

```python
def mettre_a_jour_package_json(fichier: Path, nouvelle_version: str) -> None:
    """Met à jour la version dans package.json."""
    import json
    
    with open(fichier, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    data['version'] = nouvelle_version
    
    # Préserver l'indentation (2 espaces par défaut pour NPM)
    with open(fichier, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')  # Newline final
    
    logger.log_info(f"package.json mis à jour : {nouvelle_version}")
```

#### Alternative : npm version

```python
def mettre_a_jour_package_avec_npm(nouvelle_version: str) -> None:
    """Utilise npm pour mettre à jour la version."""
    from python_commun.system.system import executer_commande_shell
    
    cmd = f"npm version {nouvelle_version} --no-git-tag-version"
    resultat = executer_commande_shell(cmd, check=True)
    
    if resultat.returncode == 0:
        logger.log_info(f"package.json mis à jour via npm : {nouvelle_version}")
```

### Rust (Cargo.toml)

```python
def mettre_a_jour_cargo_toml(fichier: Path, nouvelle_version: str) -> None:
    """Met à jour la version dans Cargo.toml."""
    import tomli
    import tomli_w
    
    with open(fichier, 'rb') as f:
        data = tomli.load(f)
    
    data['package']['version'] = nouvelle_version
    
    with open(fichier, 'wb') as f:
        tomli_w.dump(data, f)
    
    logger.log_info(f"Cargo.toml mis à jour : {nouvelle_version}")
```

### .NET (*.csproj)

```python
def mettre_a_jour_csproj(fichier: Path, nouvelle_version: str) -> None:
    """Met à jour la version dans un fichier .csproj."""
    import xml.etree.ElementTree as ET
    
    tree = ET.parse(fichier)
    root = tree.getroot()
    
    # Trouver <PropertyGroup><Version>
    for prop_group in root.findall('.//PropertyGroup'):
        version_elem = prop_group.find('Version')
        if version_elem is not None:
            version_elem.text = nouvelle_version
            break
    else:
        # Créer l'élément si absent
        prop_group = root.find('.//PropertyGroup')
        if prop_group is not None:
            version_elem = ET.SubElement(prop_group, 'Version')
            version_elem.text = nouvelle_version
    
    ET.indent(tree, space='  ')
    tree.write(fichier, encoding='utf-8', xml_declaration=True)
    
    logger.log_info(f"{fichier.name} mis à jour : {nouvelle_version}")
```

### Fonction unifiée

```python
def mettre_a_jour_version_projet(info_projet: dict, nouvelle_version: str) -> None:
    """
    Met à jour la version dans le fichier de configuration du projet.
    
    Args:
        info_projet: Résultat de detecter_type_projet()
        nouvelle_version: Nouvelle version à définir
    """
    fichier = Path(info_projet['config_file'])
    type_projet = info_projet['type']
    
    # Mapping vers les fonctions de mise à jour
    updaters = {
        'python': mettre_a_jour_pyproject_toml,
        'java': mettre_a_jour_pom_xml,
        'node': mettre_a_jour_package_json,
        'rust': mettre_a_jour_cargo_toml,
        'dotnet': mettre_a_jour_csproj,
    }
    
    if type_projet in updaters:
        updaters[type_projet](fichier, nouvelle_version)
    elif type_projet == 'git-tags':
        logger.log_info("Projet sans fichier de version")
    else:
        logger.log_warn(f"Type de projet non supporté : {type_projet}")
```

## Étape 8 : Commit & Push

### Commit des fichiers modifiés

```python
def commiter_changements_version(
    nouvelle_version: str,
    fichiers_modifies: list[str],
    message_commit_original: str
) -> None:
    """
    Commit les fichiers de version et CHANGELOG.
    
    Args:
        nouvelle_version: Version qui vient d'être appliquée
        fichiers_modifies: Liste des fichiers modifiés (pyproject.toml, CHANGELOG.md, etc.)
        message_commit_original: Message de commit généré par l'IA
    """
    import git
    
    repo = git.Repo('.')
    
    # Ajouter les fichiers de version à l'index
    repo.index.add(fichiers_modifies)
    
    # Créer le commit avec le message original
    # (le commit de versioning ne doit pas avoir son propre message)
    repo.index.commit(message_commit_original)
    
    logger.log_info(f"Commit effectué avec les fichiers de version")
```

### Push vers le dépôt distant

```python
def pousser_commit() -> None:
    """
    Pousse le commit vers le dépôt distant automatiquement.
    
    Note : Aucune confirmation n'est demandée, le push est automatique.
    """
    import git
    from python_commun.git.git_core import pousser_vers_distant
    
    repo = git.Repo('.')
    
    # Push automatique du commit
    pousser_vers_distant(repo)
    
    logger.log_success("✅ Commit poussé avec succès !")
```

## Workflow complet : Fonction principale

```python
def workflow_commit_avec_versioning(
    ia_choisie: str,
    fichiers_a_analyser: list[str],
    config_versioning: dict = None
) -> None:
    """
    Workflow complet de commit avec versioning automatique.
    
    Args:
        ia_choisie: IA à utiliser (copilot/gemini/ollama)
        fichiers_a_analyser: Fichiers à commiter
        config_versioning: Configuration optionnelle du versioning
    """
    # Configuration par défaut
    config_versioning = config_versioning or {
        'activer_versioning': True,
        'mettre_a_jour_changelog': True,
        'pousser_automatiquement': False,
        'types_sans_increment': ['docs', 'style', 'test']
    }
    
    # ===== ÉTAPE 1 : Génération du message de commit =====
    logger.log_info("📝 Génération du message de commit...")
    
    from git_ia_assistant.core.definition.ia_assistant_commit_factory import IaAssistantCommitFactory
    ia_instance = IaAssistantCommitFactory.get_commit_class(ia_choisie)
    assistant_commit = ia_instance(fichiers=fichiers_a_analyser)
    
    message_commit = assistant_commit.generer_message()
    
    # Validation par l'utilisateur
    from InquirerPy import inquirer
    choix = inquirer.select(
        message="Valider le commit ?",
        choices=[
            {"name": "✅ Oui", "value": "y"},
            {"name": "✏️  Éditer", "value": "e"},
            {"name": "❌ Annuler", "value": "n"}
        ],
        default="y"
    ).execute()
    
    if choix == "n":
        logger.log_info("Commit annulé")
        return
    elif choix == "e":
        from python_commun.git.git_core import editer_texte_avec_editeur
        message_commit = editer_texte_avec_editeur(message_commit, suffixe=".txt")
    
    # ===== ÉTAPE 2 : Détection du type de projet =====
    logger.log_info("🔍 Détection du type de projet...")
    info_projet = detecter_type_projet()
    
    logger.log_info(f"  Type : {info_projet['type']}")
    logger.log_info(f"  Version actuelle : {info_projet['current_version']}")
    
    # ===== ÉTAPE 3 : Analyse du type de modification =====
    type_commit = analyser_type_commit(message_commit)
    
    # ===== ÉTAPE 4 : Calcul de la nouvelle version =====
    if not config_versioning['activer_versioning']:
        logger.log_info("Versioning désactivé, commit simple")
        assistant_commit.valider_commit(message_commit)
        return
    
    # Vérifier si ce type de commit nécessite une incrémentation
    if type_commit['type'] in config_versioning['types_sans_increment']:
        logger.log_info(f"Type '{type_commit['type']}' : pas d'incrémentation de version")
        assistant_commit.valider_commit(message_commit)
        return
    
    nouvelle_version = calculer_nouvelle_version(
        info_projet['current_version'],
        type_commit,
        config_versioning
    )
    
    # ===== ÉTAPE 5 : Confirmation utilisateur =====
    nouvelle_version = confirmer_incrementation_version(
        info_projet['current_version'],
        nouvelle_version,
        type_commit
    )
    
    if nouvelle_version is None:
        logger.log_info("Incrémentation annulée, commit simple")
        assistant_commit.valider_commit(message_commit)
        return
    
    # ===== ÉTAPE 6 : Mise à jour du CHANGELOG.md =====
    if config_versioning['mettre_a_jour_changelog']:
        logger.log_info("📋 Mise à jour du CHANGELOG.md...")
        changelog_path = Path('CHANGELOG.md')
        mettre_a_jour_changelog(changelog_path, nouvelle_version, type_commit, message_commit)
    
    # ===== ÉTAPE 7 : Mise à jour du fichier de version =====
    logger.log_info(f"📦 Mise à jour de la version vers {nouvelle_version}...")
    mettre_a_jour_version_projet(info_projet, nouvelle_version)
    
    # ===== ÉTAPE 8 : Commit & Tag =====
    logger.log_info("💾 Commit des modifications...")
    
    # Ajouter les fichiers à l'index
    fichiers_version = [info_projet['config_file'], 'CHANGELOG.md'] if config_versioning['mettre_a_jour_changelog'] else [info_projet['config_file']]
    fichiers_version = [f for f in fichiers_version if f and Path(f).exists()]
    
    # Ajouter aussi les fichiers originaux
    from python_commun.git.git_core import ajouter_fichiers_a_index
    import git
    repo = git.Repo('.')
    ajouter_fichiers_a_index(repo, fichiers_a_analyser + fichiers_version)
    
    # Commit
    from python_commun.git.git_core import effectuer_commit_avec_message
    effectuer_commit_avec_message(repo, message_commit)
    
    # Push
    pousser_commit(config_versioning['pousser_automatiquement'])
    
    logger.log_success(f"\n✅ Commit terminé avec succès !")
    logger.log_success(f"   Version : {info_projet['current_version']} → {nouvelle_version}")
```

## Configuration du projet

### Fichier de configuration (.git-ia-assistant.toml)

```toml
[versioning]
# Activer le versioning automatique
enabled = true

# Mettre à jour CHANGELOG.md automatiquement
update_changelog = true

# Types de commits qui n'incrémentent pas la version
no_increment_for = ["docs", "style", "test", "chore", "ci"]

# Types de commits qui incrémentent PATCH
increment_patch_for = ["fix", "perf", "revert", "refactor"]

# Types de commits qui incrémentent MINOR
increment_minor_for = ["feat"]

# Respecter les BREAKING CHANGE pour MAJOR
respect_breaking_change = true

[changelog]
# Format du changelog (keepachangelog, custom)
format = "keepachangelog"

# Catégories du changelog
categories = [
    "Added",
    "Changed",
    "Fixed",
    "Deprecated",
    "Removed",
    "Security"
]

# Mapper les types de commits vers les catégories
[changelog.mapping]
feat = "Added"
fix = "Fixed"
perf = "Changed"
refactor = "Changed"
docs = "Documentation"
style = "Changed"
test = "Testing"
chore = "Maintenance"
build = "Build"
ci = "CI/CD"
revert = "Removed"
security = "Security"
```

### Chargement de la configuration

```python
def charger_configuration_versioning() -> dict:
    """
    Charge la configuration du versioning depuis .git-ia-assistant.toml
    ou retourne la configuration par défaut.
    """
    import tomli
    from pathlib import Path
    
    config_file = Path('.git-ia-assistant.toml')
    
    if not config_file.exists():
        return {
            'activer_versioning': True,
            'creer_tag': True,
            'mettre_a_jour_changelog': True,
            'pousser_automatiquement': False,
            'types_sans_increment': ['docs', 'style', 'test', 'chore', 'ci']
        }
    
    with open(config_file, 'rb') as f:
        config = tomli.load(f)
    
    return {
        'activer_versioning': config.get('versioning', {}).get('enabled', True),
        'mettre_a_jour_changelog': config.get('versioning', {}).get('update_changelog', True),
        'types_sans_increment': config.get('versioning', {}).get('no_increment_for', []),
        'increment_patch_for': config.get('versioning', {}).get('increment_patch_for', ['fix']),
        'increment_minor_for': config.get('versioning', {}).get('increment_minor_for', ['feat']),
        'respect_breaking_change': config.get('versioning', {}).get('respect_breaking_change', True),
    }
```

## Utilisation

### Commande unique

```bash
# Commit avec versioning automatique (TOUT en une commande)
git-ia-commit --version-auto
```

Cette commande unique :
1. ✅ Génère le message de commit avec l'IA
2. ✅ Détecte et incrémente automatiquement la version
3. ✅ Met à jour CHANGELOG.md
4. ✅ Commit tous les fichiers (code + version + CHANGELOG)
5. ✅ Push vers le dépôt distant

### Options supplémentaires

```bash
# Voir ce qui serait fait sans l'exécuter
git-ia-commit --version-auto --dry-run

# Choisir une IA spécifique
git-ia-commit --version-auto --ia gemini

# Commit simple sans versioning
git-ia-commit
```

### Ajout au CLI

```python
# Dans commit_cli.py, ajouter l'option
parser.add_argument(
    '--version-auto',
    action='store_true',
    help='Activer le versioning automatique (génère message, incrémente version, MAJ CHANGELOG, commit, push)'
)
```

### Point d'entrée

```python
def main() -> None:
    """Point d'entrée principal."""
    args = _parser_options()
    
    # ... code existant ...
    
    if args.version_auto:
        # WORKFLOW COMPLET EN UNE EXÉCUTION
        config = charger_configuration_versioning()
        workflow_commit_avec_versioning(ia_choisie, fichiers_a_analyser, config)
    else:
        # Workflow simple existant
        generer_et_valider_commit(ia_choisie, fichiers_a_analyser)
```

## Exemples d'utilisation

### Exemple 1 : Nouvelle fonctionnalité (MINOR)

**Commande unique :**
```bash
$ git add nouvelle_feature.py
$ git-ia-commit --version-auto
```

**Exécution automatique :**

```
📝 Génération du message de commit...
Message généré par l'IA :
feat(api): ajoute endpoint de recherche avancée

- Support des filtres par date et catégorie
- Pagination avec limite configurable
- Tri multi-critères

Valider le commit ? ✅ Oui

🔍 Détection du type de projet...
  Type : python
  Version actuelle : 0.3.0

📦 Incrémentation de version
============================================================
Version actuelle   : 0.3.0
Nouvelle version   : 0.4.0
Type de commit     : feat
Breaking change    : Non
============================================================

Incrémenter la version ? ✅ Oui, utiliser 0.4.0

📋 Mise à jour du CHANGELOG.md...
📦 Mise à jour de la version vers 0.4.0...
💾 Commit des modifications...
🚀 Push vers le dépôt distant...

✅ Commit terminé avec succès !
   Version : 0.3.0 → 0.4.0
```

**Ce qui s'est passé automatiquement :**
1. ✅ Message généré : `feat(api): ajoute endpoint...`
2. ✅ Version incrémentée : `0.3.0` → `0.4.0`
3. ✅ `CHANGELOG.md` mis à jour avec la section `[0.4.0]`
4. ✅ `pyproject.toml` mis à jour : `version = "0.4.0"`
5. ✅ Commit créé avec tous les fichiers
6. ✅ Push effectué vers `origin`
```

### Exemple 2 : Correction de bug (PATCH)

**Commande unique :**
```bash
$ git add bugfix.py
$ git-ia-commit --version-auto
```

**Résultat :**
```
Message généré :
fix(auth): corrige fuite mémoire dans le cache de session

- Nettoyage automatique des sessions expirées
- Limite de taille du cache à 1000 entrées

Version actuelle : 0.4.0
Nouvelle version : 0.4.1

✅ Commit terminé avec succès !
   Version : 0.4.0 → 0.4.1
```

**Fichiers automatiquement modifiés et commités :**
- `bugfix.py` (votre code)
- `pyproject.toml` (`version = "0.4.1"`)
- `CHANGELOG.md` (nouvelle section `[0.4.1]`)

### Exemple 3 : BREAKING CHANGE (MAJOR)

**Commande unique :**
```bash
$ git add api_v2.py
$ git-ia-commit --version-auto
```

**Résultat :**
```
Message généré :
feat(api)!: migration vers API REST v2

- Nouvelle structure de réponse JSON
- Authentification OAuth2 obligatoire
- Suppression des endpoints v1 dépréciés

BREAKING CHANGE: L'API v1 n'est plus supportée

Version actuelle : 0.4.1
Nouvelle version : 1.0.0

⚠️  ATTENTION : BREAKING CHANGE détecté !
   Cette modification nécessite un MAJOR (1.0.0)

Confirmer ? ✅ Oui

✅ Commit terminé avec succès !
   Version : 0.4.1 → 1.0.0
```

### Exemple 4 : Documentation (pas d'incrémentation)

**Commande unique :**
```bash
$ git add README.md
$ git-ia-commit --version-auto
```

**Résultat :**
```
Message généré :
docs(readme): met à jour les exemples d'utilisation

- Ajout d'exemples pour l'API v2
- Correction des liens brisés

Type 'docs' : pas d'incrémentation de version

✅ Commit effectué sans changement de version
```

**Note** : Dans ce cas, seul `README.md` est commité, pas de modification de version.

## Tests


```python
# tests/test_versioning.py

import pytest
from git_ia_assistant.versioning import (
    parser_semver,
    calculer_nouvelle_version,
    analyser_type_commit,
    valider_semver
)

def test_parser_semver_basique():
    """Test du parsing d'une version simple."""
    version = parser_semver("1.2.3")
    assert version['major'] == 1
    assert version['minor'] == 2
    assert version['patch'] == 3
    assert version['prerelease'] is None
    assert version['build'] is None

def test_parser_semver_prerelease():
    """Test du parsing avec prerelease."""
    version = parser_semver("2.0.0-alpha.1")
    assert version['major'] == 2
    assert version['minor'] == 0
    assert version['patch'] == 0
    assert version['prerelease'] == "alpha.1"

def test_parser_semver_complet():
    """Test du parsing avec prerelease et build."""
    version = parser_semver("3.1.4-beta.2+build.456")
    assert version['major'] == 3
    assert version['minor'] == 1
    assert version['patch'] == 4
    assert version['prerelease'] == "beta.2"
    assert version['build'] == "build.456"

def test_calculer_nouvelle_version_feat():
    """Test incrémentation MINOR pour feat."""
    nouvelle = calculer_nouvelle_version(
        "0.3.0",
        {'type': 'feat', 'breaking': False}
    )
    assert nouvelle == "0.4.0"

def test_calculer_nouvelle_version_fix():
    """Test incrémentation PATCH pour fix."""
    nouvelle = calculer_nouvelle_version(
        "0.3.0",
        {'type': 'fix', 'breaking': False}
    )
    assert nouvelle == "0.3.1"

def test_calculer_nouvelle_version_breaking():
    """Test incrémentation MAJOR pour BREAKING CHANGE."""
    nouvelle = calculer_nouvelle_version(
        "0.3.0",
        {'type': 'feat', 'breaking': True}
    )
    assert nouvelle == "1.0.0"

def test_analyser_type_commit_feat():
    """Test parsing d'un commit feat."""
    message = "feat(api): nouvelle fonctionnalité"
    type_commit = analyser_type_commit(message)
    
    assert type_commit['type'] == 'feat'
    assert type_commit['scope'] == 'api'
    assert type_commit['breaking'] is False
    assert type_commit['description'] == 'nouvelle fonctionnalité'

def test_analyser_type_commit_breaking():
    """Test parsing d'un BREAKING CHANGE."""
    message = """feat(api)!: migration API v2

BREAKING CHANGE: Suppression de l'API v1"""
    
    type_commit = analyser_type_commit(message)
    
    assert type_commit['type'] == 'feat'
    assert type_commit['breaking'] is True

def test_valider_semver_valides():
    """Test validation de versions valides."""
    assert valider_semver("0.0.0") is True
    assert valider_semver("1.2.3") is True
    assert valider_semver("1.0.0-alpha") is True
    assert valider_semver("2.1.3-beta.1+build.123") is True

def test_valider_semver_invalides():
    """Test validation de versions invalides."""
    assert valider_semver("1.2") is False
    assert valider_semver("v1.2.3") is False
    assert valider_semver("1.2.3.4") is False
    assert valider_semver("abc") is False
```

## Feuille de route

### Phase 1 : MVP (Minimum Viable Product)
- [x] Spécification complète
- [ ] Implémentation du versioning Python (pyproject.toml)
- [ ] Mise à jour CHANGELOG.md
- [ ] Création de tags Git
- [ ] Tests unitaires

### Phase 2 : Support multi-langage
- [ ] Support Java (pom.xml)
- [ ] Support Node.js (package.json)
- [ ] Support Rust (Cargo.toml)
- [ ] Support .NET (*.csproj)

### Phase 3 : Fonctionnalités avancées
- [ ] Gestion des monorepos (versions multiples)
- [ ] Support des prerelease (alpha, beta, rc)
- [ ] Génération de release notes depuis CHANGELOG
- [ ] Intégration avec GitHub Releases / GitLab Releases
- [ ] Webhook notifications (Slack, Teams, Discord)

### Phase 4 : Intelligence artificielle
- [ ] Détection automatique du type de commit (si message non-conventionnel)
- [ ] Suggestion de version basée sur l'analyse du diff
- [ ] Génération automatique de migration guides pour BREAKING CHANGES
- [ ] Analyse d'impact sur les dépendants du projet

## Références

- [Semantic Versioning 2.0.0](https://semver.org/)
- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/)
- [Keep a Changelog 1.0.0](https://keepachangelog.com/)
- [Git Tagging](https://git-scm.com/book/en/v2/Git-Basics-Tagging)

---

**Document rédigé le** : 2026-03-06  
**Version du document** : 1.0.0  
**Projet** : git-ia-assistant
