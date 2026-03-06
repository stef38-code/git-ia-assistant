#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    ia_assistant_review - Effectue la revue de code avec l'IA choisie (Copilot, Gemini, Ollama).

DESCRIPTION
    Script Python pour générer une revue de code à l'aide d'une IA (Copilot, Gemini, Ollama).
    
    Deux modes de fonctionnement :
    1. **Fichiers spécifiés ou modifiés** : Analyse les fichiers modifiés localement
    2. **Aucun fichier modifié** : Analyse tous les commits de la branche actuelle (par rapport à master/main)
    
    Le script utilise le prompt mr_review_prompt.md pour une analyse complète incluant :
    - Résumé exécutif et niveau de risque
    - Analyse de sécurité (OWASP Top 10)
    - Détection de bugs critiques
    - Suggestions de performance et maintenabilité
    - Tests unitaires et de sécurité manquants

OPTIONS
    fichiers                    Liste des fichiers à reviewer (optionnel)
    -ia copilot|gemini|ollama   Choix de l'IA (défaut: auto-détecté)
    -b, --base BRANCH           Branche de base pour comparer (défaut: auto-détecté master/main)
    --dry-run                   Simulation, affiche le prompt sans appel à l'IA
    -h, --help                  Afficher l'aide du script

EXEMPLES
    git-ia-review                           # Review des fichiers modifiés ou commits de la branche
    git-ia-review fichier.py                # Review d'un fichier spécifique
    git-ia-review --dry-run                 # Simulation
    git-ia-review -b develop                # Compare avec la branche develop
    git-ia-review -ia gemini fichier.py     # Utilise Gemini

FUNCTIONS
    main() : Point d'entrée du script, gère les options et le flux principal.
"""

import argparse
import os
import sys

# Ajout du chemin racine et de la librairie commune pour permettre l'import des modules du projet
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../libs/python_commun/src")))

from python_commun.git.git_core import (
    liste_fichier_non_suivis_et_modifies,
    obtenir_chemin_racine_git,
    obtenir_depot_git,
    obtenir_branche_actuelle,
)
from python_commun.ai.ia_assistant_cli_utils import detecter_ia
from python_commun.ai.prompt import charger_prompt, formatter_prompt
from python_commun.logging import logger
from python_commun.system.system import detect_lang_repo
from python_commun.ai.copilot import envoyer_prompt_copilot
from python_commun.ai.gemini import envoyer_prompt_gemini
from python_commun.ai.ollama import envoyer_prompt_ollama


def _parser_options() -> argparse.Namespace:
    """
    Analyse les options de la ligne de commande.

    :return: Un objet Namespace contenant les arguments parsés.
    """
    parser = argparse.ArgumentParser(
        description="Revue de code IA (Copilot, Gemini, Ollama)", add_help=False
    )
    parser.add_argument("fichiers", nargs="*", help="Fichiers à reviewer")
    parser.add_argument(
        "-ia",
        choices=["copilot", "gemini", "ollama"],
        default=None,
        help="Sélectionne l'IA à utiliser (défaut: auto-détection)",
    )
    parser.add_argument(
        "-b",
        "--base",
        type=str,
        default=None,
        help="Branche de base pour comparer (défaut: auto-détection master/main)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simule la review et affiche le prompt envoyé à l'IA",
    )
    parser.add_argument("-h", "--help", action="help", help="Affiche l'aide du script")
    return parser.parse_args()


def detecter_branche_base(repo) -> str:
    """
    Détecte automatiquement la branche de base (master ou main).
    
    :param repo: Objet GitPython du dépôt
    :return: Nom de la branche de base trouvée
    """
    # Priorité : origin/main, origin/master, main, master
    branches_possibles = ['origin/main', 'origin/master', 'main', 'master']
    
    for branch_name in branches_possibles:
        try:
            for ref in repo.references:
                if ref.name == branch_name:
                    return branch_name
        except Exception:
            continue
    
    # Fallback : première branche remote trouvée
    for ref in repo.references:
        if ref.name.startswith('origin/'):
            return ref.name
    
    return "master"  # Fallback ultime


def recuperer_commits_branche(repo, base_branch: str, current_branch: str) -> list:
    """
    Récupère les commits de la branche actuelle qui ne sont pas dans la branche de base.
    
    :param repo: Objet GitPython du dépôt
    :param base_branch: Nom de la branche de base
    :param current_branch: Nom de la branche actuelle
    :return: Liste des commits
    """
    try:
        # Commits dans current_branch qui ne sont pas dans base_branch
        commits = list(repo.iter_commits(f'{base_branch}..{current_branch}'))
        return commits
    except Exception as e:
        logger.log_error(f"Erreur lors de la récupération des commits : {e}")
        return []


def generer_diff_branche(repo, base_branch: str, current_branch: str) -> str:
    """
    Génère le diff complet entre la branche de base et la branche actuelle.
    
    :param repo: Objet GitPython du dépôt
    :param base_branch: Nom de la branche de base
    :param current_branch: Nom de la branche actuelle
    :return: Diff au format string
    """
    try:
        # Diff entre base_branch et current_branch
        diff = repo.git.diff(base_branch, current_branch)
        return diff
    except Exception as e:
        logger.log_error(f"Erreur lors de la génération du diff : {e}")
        return ""


def generer_diff_fichiers(repo, fichiers: list) -> str:
    """
    Génère le diff pour les fichiers modifiés spécifiés.
    
    :param repo: Objet GitPython du dépôt
    :param fichiers: Liste des fichiers à analyser
    :return: Diff au format string
    """
    try:
        # Diff des fichiers modifiés (staged + unstaged)
        diff_parts = []
        
        # Fichiers staged
        if repo.index.diff("HEAD"):
            diff_parts.append(repo.git.diff("HEAD", "--", *fichiers))
        
        # Fichiers unstaged
        if repo.index.diff(None):
            diff_parts.append(repo.git.diff("--", *fichiers))
        
        # Fichiers untracked
        untracked = [f for f in fichiers if f in repo.untracked_files]
        if untracked:
            for file in untracked:
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    diff_parts.append(f"diff --git a/{file} b/{file}\n"
                                    f"new file mode 100644\n"
                                    f"--- /dev/null\n"
                                    f"+++ b/{file}\n"
                                    f"@@ -0,0 +1,{len(content.splitlines())} @@\n"
                                    f"+{content.replace(chr(10), chr(10) + '+')}")
                except Exception:
                    pass
        
        return "\n\n".join(diff_parts)
    except Exception as e:
        logger.log_error(f"Erreur lors de la génération du diff des fichiers : {e}")
        return ""


def generer_resume_commits(commits: list) -> str:
    """
    Génère un résumé textuel des commits.
    
    :param commits: Liste des commits GitPython
    :return: Résumé formaté
    """
    if not commits:
        return "Aucun commit dans cette branche."
    
    resume_lines = [f"**{len(commits)} commit(s)** dans cette branche :\n"]
    for commit in commits:
        message_first_line = commit.message.splitlines()[0]
        resume_lines.append(f"- `{commit.hexsha[:7]}` : {message_first_line}")
    
    return "\n".join(resume_lines)


def main() -> None:
    """
    Point d'entrée principal du script.
    """
    args = _parser_options()
    repo = obtenir_depot_git()
    if not repo:
        logger.die("Le répertoire courant n'est pas un dépôt Git.")

    chemin_racine = obtenir_chemin_racine_git(repo)
    fichiers_specifies = args.fichiers
    fichiers_modifies = liste_fichier_non_suivis_et_modifies()
    
    # Déterminer le mode de fonctionnement
    mode_fichiers = bool(fichiers_specifies or fichiers_modifies)
    
    if mode_fichiers:
        # Mode 1 : Analyse des fichiers modifiés
        fichiers_a_analyser = fichiers_specifies or fichiers_modifies
        logger.log_info(f"{len(fichiers_a_analyser)} fichier(s) à analyser")
        
        diff = generer_diff_fichiers(repo, fichiers_a_analyser)
        resume = f"Analyse de {len(fichiers_a_analyser)} fichier(s) modifié(s) :\n" + "\n".join([f"- {f}" for f in fichiers_a_analyser])
        url = "Local (fichiers modifiés)"
        
    else:
        # Mode 2 : Analyse des commits de la branche
        current_branch = obtenir_branche_actuelle(repo)
        base_branch = args.base or detecter_branche_base(repo)
        
        logger.log_info(f"Aucun fichier modifié. Analyse de la branche '{current_branch}' (base: {base_branch})")
        
        commits = recuperer_commits_branche(repo, base_branch, current_branch)
        
        if not commits:
            logger.log_warn(f"Aucun commit dans la branche '{current_branch}' par rapport à '{base_branch}'.")
            logger.log_info("Astuce : Spécifiez une branche de base avec -b/--base si l'auto-détection échoue.")
            return
        
        diff = generer_diff_branche(repo, base_branch, current_branch)
        resume = generer_resume_commits(commits)
        url = f"Local (branche {current_branch} vs {base_branch})"
    
    if not diff:
        logger.log_warn("Aucun diff à analyser.")
        return
    
    # Détection du langage
    langage = detect_lang_repo(chemin_racine)
    ia_utilisee = args.ia or detecter_ia()
    
    # Chargement et formatage du prompt
    try:
        prompt_template = charger_prompt("review/mr_review_prompt.md")
    except FileNotFoundError as e:
        logger.die(f"Prompt introuvable : {e}")
        return
    
    prompt = formatter_prompt(
        prompt_template,
        url=url,
        resume=resume,
        langage=langage,
        diff=diff
    )
    
    if args.dry_run:
        logger.log_console(f"[DRYRUN] IA utilisée : {ia_utilisee}")
        logger.log_console(f"[DRYRUN] Langage détecté : {langage}")
        logger.log_console(f"[DRYRUN] Mode : {'Fichiers modifiés' if mode_fichiers else 'Commits de branche'}")
        logger.log_console(f"[DRYRUN] Prompt qui serait envoyé à l'IA :\n{prompt}")
        return
    
    # Génération de la review avec l'IA
    logger.log_info(f"Revue de code en cours avec {ia_utilisee}...")
    
    try:
        # Appel direct de l'IA avec le prompt
        if ia_utilisee == "copilot":
            review = envoyer_prompt_copilot(prompt)
        elif ia_utilisee == "gemini":
            review = envoyer_prompt_gemini(prompt)
        elif ia_utilisee == "ollama":
            review = envoyer_prompt_ollama(prompt)
        else:
            logger.die(f"IA non supportée : {ia_utilisee}")
            return
        
        if review:
            logger.log_console("\n" + "="*80)
            logger.log_console("📋 REVUE DE CODE")
            logger.log_console("="*80 + "\n")
            logger.log_console(review)
        else:
            logger.log_error("La revue générée est vide.")
    
    except Exception as e:
        logger.log_error(f"Erreur lors de la génération de la revue : {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
