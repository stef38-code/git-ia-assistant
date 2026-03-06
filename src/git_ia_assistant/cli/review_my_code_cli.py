#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    ia_assistant_review - Effectue la revue de code avec l'IA choisie (Copilot, Gemini, Ollama).

DESCRIPTION
    Script Python pour générer une revue de code à l'aide d'une IA (Copilot, Gemini, Ollama).
    
    Deux modes de fonctionnement :
    1. **Fichiers spécifiés ou modifiés** : Analyse les fichiers modifiés localement
    2. **Aucun fichier modifié** : Analyse tous les commits de la branche actuelle (par rapport à la branche parent)
    
    **Détection intelligente de la branche parent** :
    - Analyse du reflog Git pour trouver d'où la branche actuelle a été créée (checkout -b)
    - Fallback sur les branches principales si le reflog ne trouve rien (origin/main, origin/master, main, master)
    - Support des workflows complexes avec branches intermédiaires
    
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

from python_commun.cli import usage
from python_commun.git.git_core import (
    obtenir_depot_git, 
    obtenir_chemin_racine_git, 
    obtenir_branche_actuelle,
    liste_fichier_non_suivis_et_modifies,
    detecter_branche_base,
    recuperer_commits_branche,
    generer_diff_branche,
    generer_diff_fichiers,
    generer_resume_commits
)
from python_commun.ai.ia_assistant_cli_utils import detecter_ia
from python_commun.ai.prompt import charger_prompt, formatter_prompt
from python_commun.logging import logger
from python_commun.system.system import detect_lang_repo

import git


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


def _preparer_donnees_analyse(repo, args):
    """
    Prépare les données nécessaires à l'analyse (fichiers, branches).
    
    :param repo: Objet GitPython du dépôt
    :param args: Arguments de la ligne de commande
    :return: Tuple (mode_fichiers, fichiers_specifies, fichiers_modifies, base_branch)
    """
    fichiers_specifies = args.fichiers
    fichiers_modifies = liste_fichier_non_suivis_et_modifies()
    mode_fichiers = bool(fichiers_specifies or fichiers_modifies)
    
    base_branch = None
    if not mode_fichiers:
        base_branch = args.base or detecter_branche_base(repo)
    
    return mode_fichiers, fichiers_specifies, fichiers_modifies, base_branch


def _generer_diff_mode_fichiers(repo, fichiers_specifies, fichiers_modifies):
    """
    Génère le diff pour le mode fichiers modifiés.
    
    :param repo: Objet GitPython du dépôt
    :param fichiers_specifies: Fichiers spécifiés en ligne de commande
    :param fichiers_modifies: Fichiers modifiés détectés automatiquement
    :return: Tuple (diff, resume, url)
    """
    fichiers_a_analyser = fichiers_specifies or fichiers_modifies
    logger.log_info(f"{len(fichiers_a_analyser)} fichier(s) à analyser")
    
    diff = generer_diff_fichiers(repo, fichiers_a_analyser)
    resume = f"Analyse de {len(fichiers_a_analyser)} fichier(s) modifié(s) :\n" + "\n".join([f"- {f}" for f in fichiers_a_analyser])
    url = "Local (fichiers modifiés)"
    
    return diff, resume, url


def _generer_diff_mode_branche(repo, base_branch):
    """
    Génère le diff pour le mode analyse de branche.
    
    :param repo: Objet GitPython du dépôt
    :param base_branch: Nom de la branche de base
    :return: Tuple (diff, resume, url) ou None si aucun commit
    """
    current_branch = obtenir_branche_actuelle(repo)
    
    logger.log_info(f"Aucun fichier modifié. Analyse de la branche '{current_branch}' (base: {base_branch})")
    
    commits = recuperer_commits_branche(repo, base_branch, current_branch)
    
    if not commits:
        logger.log_warn(f"Aucun commit dans la branche '{current_branch}' par rapport à '{base_branch}'.")
        logger.log_info("Astuce : Spécifiez une branche de base avec -b/--base si l'auto-détection échoue.")
        return None
    
    diff = generer_diff_branche(repo, base_branch, current_branch)
    resume = generer_resume_commits(commits)
    url = f"Local (branche {current_branch} vs {base_branch})"
    
    return diff, resume, url


def _charger_et_formater_prompt(chemin_racine, url, resume, diff):
    """
    Charge le template de prompt et le formate avec les données.
    
    :param chemin_racine: Chemin racine du dépôt Git
    :param url: URL ou description de la source
    :param resume: Résumé de l'analyse
    :param diff: Diff à analyser
    :return: Prompt formaté
    """
    langage = detect_lang_repo(chemin_racine)
    
    dossier_prompts = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "prompts")
    )
    
    try:
        prompt_template = charger_prompt("review/mr_review_prompt.md", dossier_prompts)
    except FileNotFoundError as e:
        logger.die(f"Prompt introuvable : {e}")
        return None, None
    
    prompt = formatter_prompt(
        prompt_template,
        url=url,
        resume=resume,
        langage=langage,
        diff=diff
    )
    
    return prompt, langage


def _generer_review_avec_ia(prompt, ia_utilisee):
    """
    Envoie le prompt à l'IA sélectionnée et retourne la review.
    
    :param prompt: Prompt formaté à envoyer
    :param ia_utilisee: Nom de l'IA (copilot, gemini, ollama)
    :return: Review générée par l'IA
    """
    try:
        if ia_utilisee == "copilot":
            from python_commun.ai.copilot import envoyer_prompt_copilot
            return envoyer_prompt_copilot(prompt)
        elif ia_utilisee == "gemini":
            from python_commun.ai.gemini_utils import envoyer_prompt_gemini
            return envoyer_prompt_gemini(prompt)
        elif ia_utilisee == "ollama":
            from python_commun.ai.ollama_utils import appeler_ollama
            return appeler_ollama(prompt)
        else:
            logger.die(f"IA non supportée : {ia_utilisee}")
            return None
    except Exception as e:
        logger.log_error(f"Erreur lors de la génération de la revue : {e}")
        import traceback
        traceback.print_exc()
        return None


def _afficher_review(review):
    """
    Affiche la review générée par l'IA.
    
    :param review: Contenu de la review
    """
    if review:
        logger.log_console("\n" + "="*80)
        logger.log_console("📋 REVUE DE CODE")
        logger.log_console("="*80 + "\n")
        logger.log_console(review)
    else:
        logger.log_error("La revue générée est vide.")


def main() -> None:
    """
    Point d'entrée principal du script.
    """
    args = _parser_options()
    repo = obtenir_depot_git()
    if not repo:
        logger.die("Le répertoire courant n'est pas un dépôt Git.")

    chemin_racine = obtenir_chemin_racine_git(repo)
    
    # Préparation des données
    mode_fichiers, fichiers_specifies, fichiers_modifies, base_branch = _preparer_donnees_analyse(repo, args)
    
    # Génération du diff selon le mode
    if mode_fichiers:
        diff, resume, url = _generer_diff_mode_fichiers(repo, fichiers_specifies, fichiers_modifies)
    else:
        result = _generer_diff_mode_branche(repo, base_branch)
        if result is None:
            return
        diff, resume, url = result
    
    if not diff:
        logger.log_warn("Aucun diff à analyser.")
        return
    
    # Chargement et formatage du prompt
    prompt, langage = _charger_et_formater_prompt(chemin_racine, url, resume, diff)
    if prompt is None:
        return
    
    # Mode dry-run : affichage du prompt sans appel IA
    ia_utilisee = args.ia or detecter_ia()
    if args.dry_run:
        logger.log_console(f"[DRYRUN] IA utilisée : {ia_utilisee}")
        logger.log_console(f"[DRYRUN] Langage détecté : {langage}")
        logger.log_console(f"[DRYRUN] Mode : {'Fichiers modifiés' if mode_fichiers else 'Commits de branche'}")
        logger.log_console(f"[DRYRUN] Prompt qui serait envoyé à l'IA :\n{prompt}")
        return
    
    # Génération et affichage de la review
    logger.log_info(f"Revue de code en cours avec {ia_utilisee}...")
    review = _generer_review_avec_ia(prompt, ia_utilisee)
    _afficher_review(review)


if __name__ == "__main__":
    main()
