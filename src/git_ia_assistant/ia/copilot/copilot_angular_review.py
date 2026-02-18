#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    copilot_angular_review - Effectue une revue de code Angular/TS/HTML avec Copilot.

DESCRIPTION
    Ce script envoie le code Angular (TypeScript ou HTML) à Copilot pour obtenir
    une analyse sur les bugs potentiels, les optimisations et le respect des
    bonnes pratiques, en tenant compte de la version d'Angular.

SYNOPSIS
    python copilot_angular_review.py VOTRE_FICHIER [VERSION]

FUNCTIONS
    obtenir_revue_ia(chemin_fichier: str, version: str = "15", ia: str = "copilot") -> None
        Envoie le code à l'IA pour une analyse technique.
    main() -> None
        Fonction principale du script.

DATA
    __all__ = []
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import sys
from python_commun.logging.logger import logger
from python_commun.copilot import envoyer_prompt_copilot
from git_ia_assistant.copilot.copilot_utils import charger_prompt, formatter_prompt


def obtenir_revue_ia(
    chemin_fichier: str, version: str = "15", ia: str = "copilot"
) -> None:
    """
    Envoie le code à l'IA pour une analyse technique.
    :param chemin_fichier: Le chemin vers le fichier à analyser.
    :param version: La version d'Angular utilisée.
    :param ia: Nom de l'IA à utiliser.
    """
    try:
        with open(chemin_fichier, "r", encoding="utf-8") as f:
            code = f.read()
    except FileNotFoundError:
        logger.die(f"Le fichier {chemin_fichier} n'a pas été trouvé.")
        return
    prompt_template = charger_prompt("angular_review_prompt.md")
    prompt = formatter_prompt(prompt_template, code=code, version=version)
    if ia == "copilot":
        reponse = envoyer_prompt_copilot(prompt)
    else:
        reponse = "[IA non supportée]"
    logger.log_console("\n--- RETOUR DE L'IA ---")
    logger.log_console(reponse)
    logger.log_console("--------------------------\n")


def main() -> None:
    """Fonction principale."""
    if len(sys.argv) < 2:
        logger.log_warn(f"Usage: python {sys.argv[0]} VOTRE_FICHIER [VERSION]")
        sys.exit(1)
    fichier_cible = sys.argv[1]
    version = sys.argv[2] if len(sys.argv) > 2 else "15"
    obtenir_revue_ia(fichier_cible, version)


if __name__ == "__main__":
    main()
