#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    gemini_java_review - Effectue une revue de code Java avec Gemini.

DESCRIPTION
    Ce script envoie le code Java à l'API Gemini pour obtenir une analyse
    sur les bugs potentiels, les optimisations et le respect des bonnes
    pratiques, en tenant compte de la version de Java.

SYNOPSIS
    python gemini_java_review.py VOTRE_FICHIER.java [VERSION]

FUNCTIONS
    obtenir_revue_gemini(chemin_fichier: str, version: str = "17") -> None
        Envoie le code à Gemini pour une analyse technique.
    main() -> None
        Fonction principale du script.

DATA
    model: genai.GenerativeModel
        Instance du modèle Gemini configuré.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from python_commun.logging.logger import logger
from python_commun import gemini_utils

# Configuration de l'API
model = gemini_utils.configurer_gemini()


def obtenir_revue_gemini(chemin_fichier: str, version: str = "17") -> None:
    """
    Envoie le code à Gemini pour une analyse technique.

    :param chemin_fichier: Le chemin vers le fichier à analyser.
    :param version: La version de Java utilisée.
    """
    try:
        with open(chemin_fichier, "r", encoding="utf-8") as f:
            code = f.read()
    except FileNotFoundError:
        logger.die(f"Le fichier {chemin_fichier} n'a pas été trouvé.")
        return

    prompt_template = gemini_utils.charger_prompt("java_review_prompt.md")
    prompt = prompt_template.format(code=code, version=version)

    logger.log_info(f"Analyse Gemini en cours (Java {version})...")
    try:
        reponse = model.models.generate_content(
            model=gemini_utils.MODEL_NAME, contents=prompt
        )
        logger.log_console("\n--- RETOUR DE GEMINI ---")
        logger.log_console(reponse.text)
        logger.log_console("--------------------------\n")
    except Exception as e:
        logger.log_error(f"Erreur lors de l'analyse Gemini : {e}")


def main() -> None:
    """Fonction principale."""
    if len(sys.argv) < 2:
        logger.log_warn(f"Usage: python {sys.argv[0]} VOTRE_FICHIER.java [VERSION]")
        sys.exit(1)

    fichier_cible = sys.argv[1]
    version = sys.argv[2] if len(sys.argv) > 2 else "17"
    obtenir_revue_gemini(fichier_cible, version)


if __name__ == "__main__":
    main()
