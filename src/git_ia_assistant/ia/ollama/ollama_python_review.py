#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    ollama_python_review - Effectue une revue de code Python avec Ollama.

DESCRIPTION
    Ce script formate un fichier Python avec Black, puis envoie le code à
    Ollama pour obtenir une analyse sur les bugs potentiels, les optimisations
    et le respect des bonnes pratiques. Il sert de point d'entrée pour la
    revue de code Python via l'IA Ollama.

SYNOPSIS
    python ollama_python_review.py VOTRE_FICHIER.py [VERSION]

FUNCTIONS
    executer_black(chemin_fichier: str) -> bool
        Lance le formateur Black sur un fichier pour garantir un formatage propre.
    obtenir_revue_ollama(chemin_fichier: str, version: str = "3.x") -> None
        Envoie le code à Ollama pour une analyse technique et affiche le résultat.
    main() -> None
        Fonction principale du script, gère les arguments et l'exécution de la revue.

DATA
    MODELE_PYTHON: str
        Nom du modèle Ollama par défaut utilisé pour la revue Python.
"""

from python_commun.system.system import executer_capture
import sys

from python_commun.logging.logger import logger
from git_ia_assistant.ia.ollama import ollama_utils

# Modèle par défaut pour la revue Python
MODELE_PYTHON = "llama3.1"


def executer_black(chemin_fichier: str) -> bool:
    """
    Lance Black sur le fichier pour garantir un formatage propre.

    :param chemin_fichier: Le chemin vers le fichier à formater.
    :return: True si le formatage a réussi, False sinon.
    """
    logger.log_info(f"Formatage de {chemin_fichier} avec Black...")
    try:
        resultat = executer_capture([sys.executable, "-m", "black", chemin_fichier], check=False)
        if resultat.returncode != 0:
            resultat = executer_capture(["black", chemin_fichier], check=False)
    except FileNotFoundError:
        resultat = executer_capture(["black", chemin_fichier], check=False)

    if resultat.returncode != 0:
        logger.log_error(f"Erreur lors du formatage avec Black : {resultat.stderr}")
        return False
    logger.log_success("Formatage terminé.")
    return True


def obtenir_revue_ollama(chemin_fichier: str, version: str = "3.x") -> None:
    """
    Envoie le code à Ollama pour une analyse technique.

    :param chemin_fichier: Le chemin vers le fichier à analyser.
    :param version: La version de Python utilisée.
    """
    try:
        with open(chemin_fichier, "r", encoding="utf-8") as f:
            code = f.read()
    except FileNotFoundError:
        logger.die(f"Le fichier {chemin_fichier} n'a pas été trouvé.")

    prompt_template = ollama_utils.charger_prompt("python_review_prompt.md")
    prompt = prompt_template.format(code=code, version=version)

    logger.log_info(f"Analyse Ollama ({MODELE_PYTHON}) en cours...")
    try:
        reponse = ollama_utils.appeler_ollama(prompt, modele=MODELE_PYTHON)
        logger.log_console("\n--- RETOUR DE OLLAMA ---")
        logger.log_console(reponse)
        logger.log_console("--------------------------\n")
    except Exception as e:
        logger.log_error(f"Erreur lors de l'analyse Ollama : {e}")


def main() -> None:
    """Fonction principale."""
    if len(sys.argv) < 2:
        logger.log_warn(f"Usage: python {sys.argv[0]} VOTRE_FICHIER.py [VERSION]")
        sys.exit(1)

    fichier_cible = sys.argv[1]
    version = sys.argv[2] if len(sys.argv) > 2 else "3.x"
    if executer_black(fichier_cible):
        obtenir_revue_ollama(fichier_cible, version)


if __name__ == "__main__":
    main()
