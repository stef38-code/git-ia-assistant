#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    copilot_python_review - Effectue une revue de code Python avec Copilot.

DESCRIPTION
    Ce script formate un fichier Python avec Black, puis envoie le code à
    Copilot pour obtenir une analyse sur les bugs potentiels, les optimisations
    et le respect des bonnes pratiques.

SYNOPSIS
    python copilot_python_review.py VOTRE_FICHIER.py [VERSION]

FUNCTIONS
    executer_black(chemin_fichier: str) -> bool
        Lance le formateur Black sur un fichier et retourne le succès.
    obtenir_revue_ia(chemin_fichier: str, version: str = "3.x", ia: str = "copilot") -> None
        Envoie le code à l'IA et affiche l'analyse.
    main() -> None
        Fonction principale du script.

DATA
    __all__ = []
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import subprocess
import sys
from python_commun.logging.logger import logger
from python_commun.copilot import envoyer_prompt_copilot
from git_ia_assistant.copilot.copilot_utils import charger_prompt, formatter_prompt


def executer_black(chemin_fichier: str) -> bool:
    """
    Lance Black sur le fichier pour garantir un formatage propre.
    :param chemin_fichier: Le chemin vers le fichier à formater.
    :return: True si le formatage a réussi, False sinon.
    """
    logger.log_info(f"Formatage de {chemin_fichier} avec Black...")
    cmd = [sys.executable, "-m", "black", chemin_fichier]
    try:
        resultat = subprocess.run(cmd, capture_output=True, text=True)
        if resultat.returncode != 0:
            resultat = subprocess.run(
                ["black", chemin_fichier], capture_output=True, text=True
            )
    except FileNotFoundError:
        resultat = subprocess.run(
            ["black", chemin_fichier], capture_output=True, text=True
        )
    if resultat.returncode != 0:
        logger.log_error(f"Erreur lors du formatage avec Black : {resultat.stderr}")
        return False
    logger.log_success("Formatage terminé.")
    return True


def obtenir_revue_ia(
    chemin_fichier: str, version: str = "3.x", ia: str = "copilot"
) -> None:
    """
    Envoie le code à l'IA et affiche l'analyse.
    :param chemin_fichier: Le chemin vers le fichier à analyser.
    :param version: La version de Python utilisée.
    :param ia: Nom de l'IA à utiliser.
    """
    try:
        with open(chemin_fichier, "r", encoding="utf-8") as f:
            code = f.read()
    except FileNotFoundError:
        logger.die(f"Le fichier {chemin_fichier} n'a pas été trouvé.")
        return
    prompt_template = charger_prompt("python_review_prompt.md")
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
        logger.log_warn(f"Usage: python {sys.argv[0]} VOTRE_FICHIER.py [VERSION]")
        sys.exit(1)
    fichier_cible = sys.argv[1]
    version = sys.argv[2] if len(sys.argv) > 2 else "3.x"
    if executer_black(fichier_cible):
        obtenir_revue_ia(fichier_cible, version)


if __name__ == "__main__":
    main()
