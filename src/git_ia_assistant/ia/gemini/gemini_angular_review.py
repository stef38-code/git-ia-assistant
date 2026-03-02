#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    gemini_angular_review - Effectue une revue de code Angular/TS/HTML avec Gemini.

DESCRIPTION
    Ce script envoie le code Angular (TypeScript ou HTML) à l'API Gemini pour
    obtenir une analyse sur les bugs potentiels, les optimisations et le
    respect des bonnes pratiques, en tenant compte de la version d'Angular.

SYNOPSIS
    python gemini_angular_review.py VOTRE_FICHIER [VERSION]

FUNCTIONS
    obtenir_revue_gemini(chemin_fichier: str, version: str = "15") -> None
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


def obtenir_revue_gemini(chemin_fichier: str, version: str = "15") -> None:
    """
    Envoie le code à Gemini pour une analyse technique.

    :param chemin_fichier: Le chemin vers le fichier à analyser.
    :param version: La version d'Angular utilisée.
    """
    try:
        with open(chemin_fichier, "r", encoding="utf-8") as f:
            code = f.read()
    except FileNotFoundError:
        logger.die(f"Le fichier {chemin_fichier} n'a pas été trouvé.")
        return

    prompt_template = gemini_utils.charger_prompt("angular_review_prompt.md")
    prompt = prompt_template.format(code=code, version=version)

    logger.log_info(f"Analyse Gemini en cours (Angular {version})...")
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
        logger.log_warn(f"Usage: python {sys.argv[0]} VOTRE_FICHIER [VERSION]")
        sys.exit(1)

    fichier_cible = sys.argv[1]
    version = sys.argv[2] if len(sys.argv) > 2 else "15"
    obtenir_revue_gemini(fichier_cible, version)


if __name__ == "__main__":
    main()
