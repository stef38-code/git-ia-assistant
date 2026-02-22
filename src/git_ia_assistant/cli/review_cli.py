#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    ia_assistant_review - Effectue la revue de code avec l'IA choisie (Copilot, Gemini, Ollama).

DESCRIPTION
    Script Python pour générer une revue de code sur des fichiers spécifiés ou modifiés à l'aide d'une IA (Copilot, Gemini, Ollama).
    Analyse les changements, identifie les bugs potentiels et suggère des améliorations.

OPTIONS
    fichiers                    Liste des fichiers à reviewer (défaut: fichiers modifiés)
    -ia copilot|gemini|ollama   Choix de l'IA (défaut: auto-détecté)
    -l, --langage LANG          Définit le langage du projet (détection auto si absent)
    --dryrun                    Simulation, affiche le prompt sans appel à l'IA
    -h, --help                  Afficher l'aide du script

EXEMPLES
    python ia_assistant_review.py -ia gemini -l python fichier.py
    python ia_assistant_review.py --dryrun
    python ia_assistant_review.py

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
)
from python_commun.ai.ia_assistant_cli_utils import detecter_ia
from python_commun.logging import logger
from python_commun.system.system import detect_lang_repo
from git_ia_assistant.core.definition.ia_assistant_type_review_factory import (
    IaAssistantTypeReviewFactory,
)


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
        "-l",
        "--langage",
        type=str,
        default=None,
        help="Langage du projet (auto si vide)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        dest="dryrun",
        help="Simule la review et affiche le prompt envoyé à l'IA",
    )
    parser.add_argument("-h", "--help", action="help", help="Affiche l'aide du script")
    return parser.parse_args()


def main() -> None:
    """
    Point d'entrée principal du script.
    """
    args = _parser_options()
    repo = obtenir_depot_git()
    if not repo:
        logger.die("Le répertoire courant n'est pas un dépôt Git.")

    chemin_racine = obtenir_chemin_racine_git(repo)
    fichiers_git = args.fichiers or liste_fichier_non_suivis_et_modifies()

    if not fichiers_git:
        logger.log_warn("Aucun fichier à reviewer. Le script est terminé.")
        return

    ia_utilisee = args.ia or detecter_ia()
    langage_utilise = args.langage or detect_lang_repo(chemin_racine)

    review_cls = IaAssistantTypeReviewFactory.get_review_class(
        ia_utilisee, langage_utilise
    )

    if not review_cls:
        logger.die(
            f"Aucune classe de review trouvée pour la combinaison IA='{ia_utilisee}' et langage='{langage_utilise}'."
        )

    assistant = review_cls(fichiers_git, version=None)
    prompt = assistant.generer_prompt_review()

    if not prompt:
        logger.log_warn("Le prompt généré est vide, la revue est annulée.")
        return

    if args.dryrun:
        logger.log_console(f"[DRYRUN] IA utilisée : {ia_utilisee}")
        logger.log_console(f"[DRYRUN] Prompt qui serait envoyé à l'IA :\n{prompt}")
        return

    logger.log_info(f"Revue de code en cours avec {ia_utilisee}...")
    logger.log_debug(args.dryrun, f"Prompt envoyé à l'IA :\n{prompt}")
    assistant.generer_review()


if __name__ == "__main__":
    main()
