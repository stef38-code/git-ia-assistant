#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    ia_assistant_commit_version - Génère un commit avec versioning automatique et mise à jour du CHANGELOG.

DESCRIPTION
    Script Python pour générer un commit Git avec versioning automatique.
    Exécute un workflow complet en une seule commande :
    1. Génération du message de commit avec IA
    2. Détection du type de projet (Python, Java, Node.js, Go, Rust, .NET)
    3. Extraction de la version actuelle
    4. Incrémentation de version selon SemVer (feat→MINOR, fix→PATCH, BREAKING→MAJOR)
    5. Mise à jour du CHANGELOG.md
    6. Mise à jour du fichier de version (pyproject.toml, pom.xml, package.json, etc.)
    7. Commit de tous les fichiers
    8. Push vers le dépôt distant
    
    Sélection de l'IA:
      - Option --ia: choix explicite de l'IA (prioritaire si fournie)
      - Variable d'environnement IA_SELECTED: utilisée si l'option --ia est absente
      - Valeur par défaut: copilot

OPTIONS
    --ia copilot|gemini|ollama   Choix de l'IA (défaut: copilot)
    -f, --fichier <fichier(s)>  Liste des fichiers à analyser
    --dry-run                   Simulation sans appel à l'IA ni modification
    --no-version                Désactive l'incrémentation de version (commit simple)
    --no-changelog              Ne pas mettre à jour CHANGELOG.md
    -h, --help                  Afficher l'aide colorisée

VARIABLES D'ENVIRONNEMENT
    IA_SELECTED                 Choix de l'IA (copilot|gemini|ollama) utilisé uniquement si --ia est absent

EXEMPLES
    git-ia-commit-version
    git-ia-commit-version --dry-run
    git-ia-commit-version --ia gemini
    git-ia-commit-version -f fichier1.py fichier2.py
    git-ia-commit-version --no-changelog
    IA_SELECTED=gemini git-ia-commit-version

FUNCTIONS
    main() : Point d'entrée du script, gère le workflow complet de versioning.
"""

import argparse
import os
import sys
import re
from typing import List, Dict, Optional
from pathlib import Path
from datetime import date

# Ajout du chemin racine et de la librairie commune
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../libs/python_commun/src")))

from python_commun.logging import logger
from python_commun.cli.usage import usage
from python_commun.git.git_core import (
    liste_fichier_non_suivis_et_modifies,
    editer_texte_avec_editeur,
    ajouter_fichiers_a_index,
    effectuer_commit_avec_message,
    pousser_vers_distant,
    obtenir_depot_git,
)
from git_ia_assistant.core.definition.ia_assistant_commit_factory import (
    IaAssistantCommitFactory,
)


def _parser_options() -> argparse.Namespace:
    """
    Analyse et retourne les arguments de la ligne de commande.

    :return: Un objet Namespace contenant les arguments parsés.
    """
    parser = argparse.ArgumentParser(
        add_help=False, 
        description="Génère un commit avec versioning automatique."
    )
    parser.add_argument(
        "--ia",
        choices=["copilot", "gemini", "ollama"],
        default="copilot",
        help="IA à utiliser (défaut: copilot)",
    )
    parser.add_argument(
        "-f", "--fichier", nargs="*", help="Nom(s) de fichier à analyser"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Simulation sans modification"
    )
    parser.add_argument(
        "--no-version", action="store_true", help="Désactive l'incrémentation de version"
    )
    parser.add_argument(
        "--no-changelog", action="store_true", help="Ne pas mettre à jour CHANGELOG.md"
    )
    parser.add_argument(
        "-h", "--help", action="store_true", help="Afficher l'aide colorisée"
    )
    return parser.parse_args()


# ==================== CONFIGURATION DES PROJETS ====================

PROJECT_CONFIGS = {
    "python": [
        {
            "file": "pyproject.toml",
            "version_pattern": r'version\s*=\s*"([0-9]+\.[0-9]+\.[0-9]+.*)"',
            "update_key": "version"
        },
        {
            "file": "setup.py",
            "version_pattern": r'version\s*=\s*["\']([0-9]+\.[0-9]+\.[0-9]+.*)["\']',
        }
    ],
    "java": [
        {
            "file": "pom.xml",
            "version_pattern": r'<version>([0-9]+\.[0-9]+\.[0-9]+.*)</version>',
        },
        {
            "file": "build.gradle",
            "version_pattern": r'version\s*[=:]\s*["\']([0-9]+\.[0-9]+\.[0-9]+.*)["\']',
        }
    ],
    "node": [
        {
            "file": "package.json",
            "json_key": "version"
        }
    ],
    "rust": [
        {
            "file": "Cargo.toml",
            "version_pattern": r'version\s*=\s*"([0-9]+\.[0-9]+\.[0-9]+.*)"',
        }
    ],
    "dotnet": [
        {
            "file_pattern": "*.csproj",
            "version_pattern": r'<Version>([0-9]+\.[0-9]+\.[0-9]+.*)</Version>',
        }
    ]
}


# ==================== VALIDATION SEMVER ====================

def valider_semver(version: str) -> bool:
    """
    Valide qu'une version respecte le format SemVer.
    
    :param version: Version à valider
    :return: True si valide, False sinon
    """
    pattern = r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)' \
              r'(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)' \
              r'(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?' \
              r'(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'
    
    return bool(re.match(pattern, version))


def parser_semver(version: str) -> Dict[str, any]:
    """
    Parse une version SemVer.
    
    :param version: Version à parser
    :return: Dictionnaire avec major, minor, patch, prerelease, build
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


# ==================== DÉTECTION DU PROJET ====================

def detecter_type_projet() -> Optional[Dict]:
    """
    Détecte le type de projet et retourne la configuration.
    
    :return: Dictionnaire avec type, config_file, current_version
    """
    try:
        repo = obtenir_depot_git()
        if not repo:
            logger.log_error("Pas de dépôt Git détecté")
            return None
        
        racine_git = Path(repo.working_dir)
    except Exception as e:
        logger.log_error(f"Erreur lors de la détection du dépôt Git : {e}")
        return None
    
    # Parcourir les configurations par type de projet
    for project_type, configs in PROJECT_CONFIGS.items():
        for config in configs:
            # Gérer les patterns de fichiers (*.csproj)
            if "file_pattern" in config:
                matches = list(racine_git.glob(config["file_pattern"]))
                if matches:
                    config_path = matches[0]
                else:
                    continue
            else:
                config_path = racine_git / config["file"]
            
            if config_path.exists():
                version = extraire_version(config_path, config)
                if version:
                    return {
                        'type': project_type,
                        'config_file': str(config_path),
                        'config': config,
                        'current_version': version
                    }
    
    logger.log_warn("Type de projet non détecté, versioning désactivé")
    return None


def extraire_version(fichier: Path, config: Dict) -> Optional[str]:
    """
    Extrait la version depuis un fichier de configuration.
    
    :param fichier: Chemin du fichier
    :param config: Configuration du parsing
    :return: Version extraite ou None
    """
    try:
        # Fichier JSON (package.json)
        if "json_key" in config:
            import json
            with open(fichier, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get(config["json_key"])
        
        # Fichier TOML (pyproject.toml, Cargo.toml)
        elif str(fichier).endswith('.toml'):
            try:
                import tomli
            except ImportError:
                import tomllib as tomli
            
            with open(fichier, 'rb') as f:
                data = tomli.load(f)
            
            # Pour pyproject.toml
            if 'project' in data and 'version' in data['project']:
                return data['project']['version']
            # Pour Cargo.toml
            elif 'package' in data and 'version' in data['package']:
                return data['package']['version']
        
        # Fichier avec pattern regex
        elif "version_pattern" in config:
            with open(fichier, 'r', encoding='utf-8') as f:
                contenu = f.read()
            
            match = re.search(config["version_pattern"], contenu)
            if match:
                return match.group(1)
        
    except Exception as e:
        logger.log_warn(f"Erreur lors de l'extraction de version depuis {fichier} : {e}")
    
    return None


# ==================== ANALYSE DU COMMIT ====================

def analyser_type_commit(message: str) -> Dict:
    """
    Analyse un message de commit Conventional Commits.
    
    :param message: Message de commit
    :return: Dictionnaire avec type, scope, breaking, description, body
    """
    # Pattern Conventional Commits
    pattern = r'^(?P<type>\w+)(?:\((?P<scope>[^)]+)\))?(?P<breaking>!)?: (?P<description>.+)$'
    
    lignes = message.strip().split('\n')
    premiere_ligne = lignes[0]
    
    match = re.match(pattern, premiere_ligne)
    if not match:
        return {
            'type': 'chore',
            'scope': None,
            'breaking': False,
            'description': premiere_ligne,
            'body': ''
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


# ==================== CALCUL DE VERSION ====================

def calculer_nouvelle_version(version_actuelle: str, type_commit: Dict) -> str:
    """
    Calcule la nouvelle version selon les règles SemVer.
    
    :param version_actuelle: Version actuelle
    :param type_commit: Résultat de analyser_type_commit()
    :return: Nouvelle version
    """
    # Configuration par défaut
    increment_patch_for = ['fix', 'perf', 'revert']
    increment_minor_for = ['feat']
    no_increment_for = ['docs', 'style', 'test', 'chore', 'ci', 'build', 'refactor']
    
    version = parser_semver(version_actuelle)
    
    # BREAKING CHANGE → MAJOR
    if type_commit['breaking']:
        version['major'] += 1
        version['minor'] = 0
        version['patch'] = 0
    
    # feat → MINOR
    elif type_commit['type'] in increment_minor_for:
        version['minor'] += 1
        version['patch'] = 0
    
    # fix, perf → PATCH
    elif type_commit['type'] in increment_patch_for:
        version['patch'] += 1
    
    # docs, style, etc. → Pas d'incrémentation
    elif type_commit['type'] in no_increment_for:
        return version_actuelle
    
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


def confirmer_incrementation_version(version_actuelle: str, nouvelle_version: str, type_commit: Dict) -> Optional[str]:
    """
    Demande confirmation à l'utilisateur pour l'incrémentation de version.
    
    :return: Version confirmée ou None si annulé
    """
    from InquirerPy import inquirer
    
    print(f"\n{'='*60}")
    print(f"📦 Incrémentation de version")
    print(f"{'='*60}")
    print(f"Version actuelle   : {version_actuelle}")
    print(f"Nouvelle version   : {nouvelle_version}")
    print(f"Type de commit     : {type_commit['type']}")
    print(f"Breaking change    : {'Oui' if type_commit['breaking'] else 'Non'}")
    print(f"{'='*60}\n")
    
    if type_commit['breaking']:
        logger.log_warn("⚠️  ATTENTION : BREAKING CHANGE détecté !")
        logger.log_warn(f"   Cette modification nécessite un MAJOR ({nouvelle_version})")
    
    choix = inquirer.select(
        message="Incrémenter la version ?",
        choices=[
            {"name": f"✅ Oui, utiliser {nouvelle_version}", "value": "yes"},
            {"name": "✏️  Modifier manuellement", "value": "edit"},
            {"name": "❌ Non, ne pas incrémenter", "value": "no"},
        ],
        default="yes"
    ).execute()
    
    if choix == "yes":
        return nouvelle_version
    elif choix == "edit":
        return saisir_version_manuelle(version_actuelle)
    else:
        return None


def saisir_version_manuelle(version_actuelle: str) -> str:
    """Permet à l'utilisateur de saisir manuellement une version."""
    from InquirerPy import inquirer
    
    while True:
        version = inquirer.text(
            message=f"Nouvelle version (actuelle: {version_actuelle})",
            default=version_actuelle,
            validate=lambda v: valider_semver(v) or "Format invalide (ex: 1.0.0)"
        ).execute()
        
        if valider_semver(version):
            return version


# ==================== MISE À JOUR DU CHANGELOG ====================

def mettre_a_jour_changelog(
    fichier_changelog: Path,
    nouvelle_version: str,
    type_commit: Dict,
    message_commit: str
) -> None:
    """
    Met à jour CHANGELOG.md avec la nouvelle version.
    
    :param fichier_changelog: Chemin vers CHANGELOG.md
    :param nouvelle_version: Version à ajouter
    :param type_commit: Résultat de analyser_type_commit()
    :param message_commit: Message de commit complet
    """
    # Mapper le type de commit vers la catégorie du changelog
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
    
    categorie = MAPPING_CATEGORIES.get(type_commit['type'], 'Changed')
    
    # Si BREAKING CHANGE, ajouter aussi dans Security
    if type_commit['breaking']:
        categorie = 'Security'
    
    # Extraire les points du body
    body_lines = type_commit.get('body', '').strip().split('\n')
    points = [
        ligne.strip('- ').strip()
        for ligne in body_lines
        if ligne.strip().startswith('-')
    ]
    
    # Si pas de points dans le body, utiliser la description
    if not points:
        points = [type_commit['description']]
    
    # Créer la nouvelle entrée
    nouvelle_entree = f"""## [{nouvelle_version}] - {date.today()}

### {categorie}
"""
    for point in points:
        nouvelle_entree += f"- {point}\n"
    
    nouvelle_entree += "\n"
    
    # Insérer dans le changelog
    if not fichier_changelog.exists():
        # Créer un nouveau changelog
        contenu = f"""# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
et ce projet adhère à [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

{nouvelle_entree}"""
    else:
        # Insérer après l'en-tête
        with open(fichier_changelog, 'r', encoding='utf-8') as f:
            contenu = f.read()
        
        # Trouver la position d'insertion (après le préambule)
        pattern = r'(# Changelog.*?adhère à.*?\n\n)'
        match = re.search(pattern, contenu, re.DOTALL)
        
        if match:
            position = match.end()
            contenu = contenu[:position] + nouvelle_entree + contenu[position:]
        else:
            # Fallback : insérer au début
            contenu = nouvelle_entree + contenu
    
    # Écrire le fichier
    with open(fichier_changelog, 'w', encoding='utf-8') as f:
        f.write(contenu)
    
    logger.log_info(f"CHANGELOG.md mis à jour avec la version {nouvelle_version}")


# ==================== MISE À JOUR DE LA VERSION ====================

def mettre_a_jour_version_python(fichier: Path, nouvelle_version: str) -> None:
    """Met à jour la version dans pyproject.toml."""
    try:
        import tomli
    except ImportError:
        import tomllib as tomli
    
    try:
        import tomli_w
    except ImportError:
        logger.log_error("tomli_w non installé. Installez avec: pip install tomli-w")
        # Fallback : modification manuelle avec regex
        with open(fichier, 'r', encoding='utf-8') as f:
            contenu = f.read()
        
        contenu = re.sub(
            r'(version\s*=\s*")[^"]+(")',
            rf'\g<1>{nouvelle_version}\g<2>',
            contenu
        )
        
        with open(fichier, 'w', encoding='utf-8') as f:
            f.write(contenu)
        
        logger.log_info(f"pyproject.toml mis à jour : {nouvelle_version}")
        return
    
    with open(fichier, 'rb') as f:
        data = tomli.load(f)
    
    data['project']['version'] = nouvelle_version
    
    with open(fichier, 'wb') as f:
        tomli_w.dump(data, f)
    
    logger.log_info(f"pyproject.toml mis à jour : {nouvelle_version}")


def mettre_a_jour_version_node(fichier: Path, nouvelle_version: str) -> None:
    """Met à jour la version dans package.json."""
    import json
    
    with open(fichier, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    data['version'] = nouvelle_version
    
    with open(fichier, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')
    
    logger.log_info(f"package.json mis à jour : {nouvelle_version}")


def mettre_a_jour_version_fichier(fichier: Path, nouvelle_version: str, config: Dict) -> None:
    """Met à jour la version dans un fichier générique avec regex."""
    with open(fichier, 'r', encoding='utf-8') as f:
        contenu = f.read()
    
    if "version_pattern" in config:
        # Remplacer la première occurrence
        contenu = re.sub(
            config["version_pattern"],
            lambda m: m.group(0).replace(m.group(1), nouvelle_version),
            contenu,
            count=1
        )
    
    with open(fichier, 'w', encoding='utf-8') as f:
        f.write(contenu)
    
    logger.log_info(f"{fichier.name} mis à jour : {nouvelle_version}")


def mettre_a_jour_version_projet(info_projet: Dict, nouvelle_version: str) -> None:
    """
    Met à jour la version dans le fichier de configuration du projet.
    
    :param info_projet: Résultat de detecter_type_projet()
    :param nouvelle_version: Nouvelle version à définir
    """
    fichier = Path(info_projet['config_file'])
    type_projet = info_projet['type']
    config = info_projet['config']
    
    # Mapping vers les fonctions de mise à jour
    if type_projet == 'python' and str(fichier).endswith('.toml'):
        mettre_a_jour_version_python(fichier, nouvelle_version)
    elif type_projet == 'node':
        mettre_a_jour_version_node(fichier, nouvelle_version)
    else:
        mettre_a_jour_version_fichier(fichier, nouvelle_version, config)


# ==================== WORKFLOW PRINCIPAL ====================

def workflow_commit_avec_versioning(
    ia_choisie: str,
    fichiers_a_analyser: List[str],
    dry_run: bool = False,
    activer_versioning: bool = True,
    mettre_a_jour_changelog: bool = True
) -> None:
    """
    Workflow complet de commit avec versioning automatique.
    
    :param ia_choisie: IA à utiliser (copilot/gemini/ollama)
    :param fichiers_a_analyser: Fichiers à commiter
    :param dry_run: Mode simulation
    :param activer_versioning: Activer le versioning
    :param mettre_a_jour_changelog: Mettre à jour CHANGELOG.md
    """
    # ===== ÉTAPE 1 : Génération du message de commit =====
    logger.log_info("📝 Génération du message de commit...")
    
    ia_instance = IaAssistantCommitFactory.get_commit_class(ia_choisie)
    assistant_commit = ia_instance(fichiers=fichiers_a_analyser)
    
    if dry_run:
        logger.log_info("[DRY-RUN] Mode simulation activé")
        message_commit = assistant_commit.generer_message()
        logger.log_info(f"\nMessage généré :\n{message_commit}")
        
        if activer_versioning:
            info_projet = detecter_type_projet()
            if info_projet:
                type_commit = analyser_type_commit(message_commit)
                nouvelle_version = calculer_nouvelle_version(
                    info_projet['current_version'],
                    type_commit
                )
                logger.log_info(f"\n[DRY-RUN] Version actuelle : {info_projet['current_version']}")
                logger.log_info(f"[DRY-RUN] Nouvelle version : {nouvelle_version}")
        
        logger.log_info("\n[DRY-RUN] Simulation terminée, aucune modification effectuée")
        return
    
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
        message_commit = editer_texte_avec_editeur(message_commit, suffixe=".txt")
    
    # ===== ÉTAPE 2 : Détection du type de projet =====
    if not activer_versioning:
        logger.log_info("Versioning désactivé, commit simple")
        repo = obtenir_depot_git()
        ajouter_fichiers_a_index(repo, fichiers_a_analyser)
        effectuer_commit_avec_message(repo, message_commit)
        
        pousser = inquirer.confirm(
            message="Pousser le commit vers le dépôt distant ?",
            default=True
        ).execute()
        
        if pousser:
            pousser_vers_distant(repo)
            logger.log_success("✅ Commit poussé avec succès !")
        
        return
    
    logger.log_info("🔍 Détection du type de projet...")
    info_projet = detecter_type_projet()
    
    if not info_projet:
        logger.log_warn("Type de projet non détecté, commit simple sans versioning")
        repo = obtenir_depot_git()
        ajouter_fichiers_a_index(repo, fichiers_a_analyser)
        effectuer_commit_avec_message(repo, message_commit)
        pousser_vers_distant(repo)
        logger.log_success("✅ Commit terminé avec succès !")
        return
    
    logger.log_info(f"  Type : {info_projet['type']}")
    logger.log_info(f"  Version actuelle : {info_projet['current_version']}")
    
    # ===== ÉTAPE 3 : Analyse du type de modification =====
    type_commit = analyser_type_commit(message_commit)
    
    # ===== ÉTAPE 4 : Calcul de la nouvelle version =====
    nouvelle_version = calculer_nouvelle_version(
        info_projet['current_version'],
        type_commit
    )
    
    # Vérifier si ce type de commit nécessite une incrémentation
    if nouvelle_version == info_projet['current_version']:
        logger.log_info(f"Type '{type_commit['type']}' : pas d'incrémentation de version")
        repo = obtenir_depot_git()
        ajouter_fichiers_a_index(repo, fichiers_a_analyser)
        effectuer_commit_avec_message(repo, message_commit)
        pousser_vers_distant(repo)
        logger.log_success("✅ Commit terminé avec succès !")
        return
    
    # ===== ÉTAPE 5 : Confirmation utilisateur =====
    nouvelle_version = confirmer_incrementation_version(
        info_projet['current_version'],
        nouvelle_version,
        type_commit
    )
    
    if nouvelle_version is None:
        logger.log_info("Incrémentation annulée, commit simple")
        repo = obtenir_depot_git()
        ajouter_fichiers_a_index(repo, fichiers_a_analyser)
        effectuer_commit_avec_message(repo, message_commit)
        pousser_vers_distant(repo)
        logger.log_success("✅ Commit terminé avec succès !")
        return
    
    # ===== ÉTAPE 6 : Mise à jour du CHANGELOG.md =====
    fichiers_version = []
    
    if mettre_a_jour_changelog:
        logger.log_info("📋 Mise à jour du CHANGELOG.md...")
        changelog_path = Path('CHANGELOG.md')
        mettre_a_jour_changelog(changelog_path, nouvelle_version, type_commit, message_commit)
        fichiers_version.append('CHANGELOG.md')
    
    # ===== ÉTAPE 7 : Mise à jour du fichier de version =====
    logger.log_info(f"📦 Mise à jour de la version vers {nouvelle_version}...")
    mettre_a_jour_version_projet(info_projet, nouvelle_version)
    fichiers_version.append(info_projet['config_file'])
    
    # ===== ÉTAPE 8 : Commit & Push =====
    logger.log_info("💾 Commit des modifications...")
    
    repo = obtenir_depot_git()
    
    # Ajouter tous les fichiers
    tous_fichiers = fichiers_a_analyser + fichiers_version
    ajouter_fichiers_a_index(repo, tous_fichiers)
    
    # Commit
    effectuer_commit_avec_message(repo, message_commit)
    
    # Push automatique
    logger.log_info("🚀 Push vers le dépôt distant...")
    pousser_vers_distant(repo)
    
    logger.log_success(f"\n✅ Commit terminé avec succès !")
    logger.log_success(f"   Version : {info_projet['current_version']} → {nouvelle_version}")


def main() -> None:
    """Point d'entrée principal du script."""
    args = _parser_options()
    
    # Afficher l'aide si demandé
    if getattr(args, "help", False):
        usage(__file__)
        return
    
    # Déterminer l'IA à utiliser
    ia_choisie = args.ia
    if not ia_choisie:
        ia_choisie = os.getenv("IA_SELECTED", "copilot")
    
    # Déterminer les fichiers à analyser
    fichiers_a_analyser = args.fichier
    if not fichiers_a_analyser:
        fichiers_a_analyser = liste_fichier_non_suivis_et_modifies()
        if fichiers_a_analyser:
            logger.log_info(
                f"{len(fichiers_a_analyser)} fichier(s) modifié(s) ou non suivi(s) détecté(s)."
            )
    
    if not fichiers_a_analyser:
        logger.log_warn("Aucun fichier à commiter. Le script est terminé.")
        return
    
    # Exécuter le workflow
    workflow_commit_avec_versioning(
        ia_choisie=ia_choisie,
        fichiers_a_analyser=fichiers_a_analyser,
        dry_run=args.dry_run,
        activer_versioning=not args.no_version,
        mettre_a_jour_changelog=not args.no_changelog
    )


if __name__ == "__main__":
    main()
