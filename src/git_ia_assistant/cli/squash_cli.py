#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    ia_assistant_squash - Script principal pour la suggestion de squash IA.

DESCRIPTION
    Génère une suggestion de squash de commits via une IA sélectionnable.

OPTIONS
    -ia {copilot,gemini,ollama}   Sélectionne l'IA à utiliser (défaut: auto-détection)
    -c, --commits N               Nombre de commits à traiter (défaut: 10)
    --dry-run                     Simule sans modification et affiche le prompt généré

EXEMPLES
    # Utilise Gemini pour les 5 derniers commits
    python ia_assistant_squash.py -ia gemini -c 5
    # Simule la génération du prompt pour les 10 derniers commits
    python ia_assistant_squash.py --dry-run
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from python_commun.ai.git_ia_assistant.cli_utils import detecter_ia
from python_commun.logging import logger
from git_ia_assistant.core.definition.ia_assistant_squash_factory import (
    IaAssistantSquashFactory,
)


def _parser_options() -> argparse.Namespace:
    """
    Analyse les options de la ligne de commande.

    :return: Un objet Namespace contenant les arguments parsés.
    """
    parser = argparse.ArgumentParser(
        description="Suggestion de squash IA (Copilot, Gemini, Ollama)"
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
        "--dry-run",
        action="store_true",
        help="Simule sans modification et affiche le prompt généré",
    )
    return parser.parse_args()


def main() -> None:
    """
    Point d'entrée principal du script.
    """
    args = _parser_options()
    nom_ia = args.ia or detecter_ia()
    nombre_commits = args.commits

    try:
        classe_squash = IaAssistantSquashFactory.get_squash_class(nom_ia)
        assistant_ia = classe_squash(nombre_commits)

        liste_commits = assistant_ia.recuperer_commits()
        if not liste_commits:
            logger.log_warn("Aucun commit à analyser.")
            return

        prompt_genere = assistant_ia.generer_prompt(liste_commits)

        if args.dry_run:
            logger.log_console(f"[DRY-RUN] IA utilisée : {nom_ia}")
            logger.log_console(f"[DRY-RUN] Prompt qui serait généré :\n{prompt_genere}")
            return

        logger.log_info(f"Génération de la suggestion de squash avec {nom_ia}...")
        suggestion_squash = assistant_ia.generer_squash(liste_commits)

        logger.log_console(f"\nIA utilisée : {nom_ia}")
        logger.log_debug(args.dry_run, f"Prompt envoyé à l'IA :\n{prompt_genere}")
        logger.log_console("\n" + "=" * 30 + " SUGGESTION DE SQUASH " + "=" * 30)
        logger.log_console(suggestion_squash)
        logger.log_console("=" * (78))

    except ValueError as e:
        logger.die(f"Erreur : {e}")
    except Exception as e:
        logger.die(f"Une erreur inattendue est survenue : {e}")


if __name__ == "__main__":
    main()
