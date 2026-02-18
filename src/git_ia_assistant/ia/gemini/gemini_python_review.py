#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    gemini_python_review - Effectue une revue de code Python avec Gemini.

DESCRIPTION
    Ce script formate un fichier Python avec Black, puis envoie le code à
    l'API Gemini pour obtenir une analyse sur les bugs potentiels, les
    optimisations et le respect des bonnes pratiques.

SYNOPSIS
    python gemini_python_review.py VOTRE_FICHIER.py [VERSION]

FUNCTIONS
    executer_black(chemin_fichier: str) -> bool
        Lance le formateur Black sur le fichier.
    obtenir_revue_gemini(chemin_fichier: str, version: str = "3.x") -> None
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

import subprocess

from python_commun.logging.logger import logger
from python_commun import gemini_utils

# Configuration de l'API
model = gemini_utils.configurer_gemini()


def executer_black(chemin_fichier: str) -> bool:
    """
    Lance Black sur le fichier pour garantir un formatage propre.

    :param chemin_fichier: Le chemin vers le fichier à formater.
    :return: True si le formatage a réussi, False sinon.
    """
    logger.log_info(f"Formatage de {chemin_fichier} avec Black...")
    # Tentative d'appel de black via l'interpréteur actuel ou via l'exécutable black
    cmd = [sys.executable, "-m", "black", chemin_fichier]
    try:
        resultat = subprocess.run(cmd, capture_output=True, text=True)
        if resultat.returncode != 0:
            # Si -m black échoue, on tente l'exécutable direct
            resultat = subprocess.run(
                ["black", chemin_fichier], capture_output=True, text=True
            )
    except FileNotFoundError:
        # Fallback sur l'exécutable black si python -m black échoue par FileNotFoundError
        resultat = subprocess.run(
            ["black", chemin_fichier], capture_output=True, text=True
        )

    if resultat.returncode != 0:
        logger.log_error(f"Erreur lors du formatage avec Black : {resultat.stderr}")
        return False
    logger.log_success("Formatage terminé.")
    return True


def obtenir_revue_gemini(chemin_fichier: str, version: str = "3.x") -> None:
    """
    Envoie le code à Gemini pour une analyse technique.

    :param chemin_fichier: Le chemin vers le fichier à analyser.
    :param version: La version de Python utilisée.
    """
    try:
        with open(chemin_fichier, "r", encoding="utf-8") as f:
            code = f.read()
    except FileNotFoundError:
        logger.die(f"Le fichier {chemin_fichier} n'a pas été trouvé.")
        return

    prompt_template = gemini_utils.charger_prompt("python_review_prompt.md")
    prompt = prompt_template.format(code=code, version=version)

    logger.log_info("Analyse Gemini en cours...")
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
        logger.log_warn(f"Usage: python {sys.argv[0]} VOTRE_FICHIER.py [VERSION]")
        sys.exit(1)

    fichier_cible = sys.argv[1]
    version = sys.argv[2] if len(sys.argv) > 2 else "3.x"
    if executer_black(fichier_cible):
        obtenir_revue_gemini(fichier_cible, version)


if __name__ == "__main__":
    # Pour que ce script fonctionne, il doit être lancé depuis la racine du
    # projet, ou le module 'commun' doit être dans le PYTHONPATH.
    main()
