#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    ia_assistant_changelog - Génère un changelog avec l'IA choisie (Copilot, Gemini, Ollama).

DESCRIPTION
    Script Python pour générer un changelog Git à partir des commits à l'aide d'une IA (Copilot, Gemini, Ollama).
    Permet de récupérer les commits récents et de générer un résumé des changements.

OPTIONS
    -ia copilot|gemini|ollama   Choix de l'IA (défaut: auto-détecté)
    -c, --commits N             Nombre de commits à traiter (défaut: 10)
    --dryrun                    Simulation, affiche le prompt sans appel à l'IA
    -h, --help                  Afficher l'aide du script

EXEMPLES
    python ia_assistant_changelog.py -ia gemini -c 5
    python ia_assistant_changelog.py --dryrun
    python ia_assistant_changelog.py -c 20

FUNCTIONS
    main() : Point d'entrée du script, gère les options et le flux principal.
"""

import argparse
import os
import sys
from typing import List, Tuple

# Ajout du chemin racine et de la librairie commune pour permettre l'import des modules du projet
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../libs/python_commun/src")))

from git_ia_assistant.core.definition.ia_assistant_changelog_factory import (
    IaAssistantChangelogFactory,
)
from python_commun.ai.ia_assistant_cli_utils import  detecter_ia
from python_commun.logging import logger


def _parser_options() -> Tuple[argparse.Namespace, List[str]]:
    """
    Analyse les options de la ligne de commande.

    :return: Un tuple contenant les arguments parsés et les arguments inconnus.
    """
    parser = argparse.ArgumentParser(
        description="Génération de changelog IA (Copilot, Gemini, Ollama)",
        add_help=False,
    )
    parser.add_argument(
        "-ia",
        choices=["copilot", "gemini", "ollama"],
        default=None,
        help="Sélectionne l'IA à utiliser (défaut: auto-détection)",
    )
    parser.add_argument(
        "-c",
        "--commits",
        type=int,
        default=10,
        help="Nombre de commits à traiter (défaut: 10)",
    )
    parser.add_argument(
        "--dryrun",
        "--dry-run",
        action="store_true",
        dest="dryrun",
        help="Simule la génération et affiche le prompt envoyé à l'IA",
    )
    parser.add_argument("-h", "--help", action="help", help="Affiche l'aide du script")
    return parser.parse_known_args()


def main() -> None:
    """
    Point d'entrée principal du script.
    """
    args, _ = _parser_options()

    # Détermine l'IA à utiliser : argument, sinon détection auto
    ia_utilisee = args.ia or detecter_ia()
    nombre_commits = args.commits

    try:
        # Utilisation de la factory pour obtenir la classe appropriée
        changelog_cls = IaAssistantChangelogFactory.get_changelog_class(ia_utilisee)
        assistant = changelog_cls(nombre_commits)

        messages = assistant.recuperer_commits()
        prompt = assistant.generer_prompt(messages)

        if args.dryrun:
            logger.log_console(f"[DRYRUN] IA utilisée : {ia_utilisee}")
            logger.log_console(f"[DRYRUN] Prompt qui serait envoyé à l'IA :\n{prompt}")
            return

        # Génération et affichage du changelog
        logger.log_info(f"Génération du changelog avec {ia_utilisee}...")
        changelog = assistant.generer_changelog(messages)

        logger.log_console("\n" + "=" * 30 + " CHANGELOG GÉNÉRÉ " + "=" * 30)
        logger.log_console(changelog)
        logger.log_console("=" * (78))

    except ValueError as e:
        logger.die(f"Erreur : {e}")
    except Exception as e:
        logger.die(f"Une erreur inattendue est survenue : {e}")


if __name__ == "__main__":
    main()
