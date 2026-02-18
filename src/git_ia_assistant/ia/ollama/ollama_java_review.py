#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    ollama_java_review - Effectue une revue de code Java avec Ollama.

DESCRIPTION
    Ce script envoie le code Java à Ollama pour obtenir une analyse sur les
    bugs potentiels, les optimisations et le respect des bonnes pratiques.
    Il sert de point d'entrée pour la revue de code Java via l'IA Ollama.

SYNOPSIS
    python ollama_java_review.py VOTRE_FICHIER.java [VERSION]

FUNCTIONS
    obtenir_revue_ollama(chemin_fichier: str, version: str = "17") -> None
        Envoie le code à Ollama pour une analyse technique et affiche le résultat.
    main() -> None
        Fonction principale du script, gère les arguments et l'exécution de la revue.

DATA
    MODELE_JAVA: str
        Nom du modèle Ollama par défaut utilisé pour la revue Java.
"""

import sys

from python_commun.logging.logger import logger
from git_ia_assistant.ia.ollama import ollama_utils

# Modèle par défaut pour la revue Java (CodeQwen est excellent pour ça)
MODELE_JAVA = "codeqwen"


def obtenir_revue_ollama(chemin_fichier: str, version: str = "17") -> None:
    """
    Envoie le code à Ollama pour une analyse technique.

    :param chemin_fichier: Le chemin vers le fichier à analyser.
    :param version: La version de Java utilisée.
    """
    try:
        with open(chemin_fichier, "r", encoding="utf-8") as f:
            code = f.read()
    except FileNotFoundError:
        logger.die(f"Le fichier {chemin_fichier} n'a pas été trouvé.")

    prompt_template = ollama_utils.charger_prompt("java_review_prompt.md")
    prompt = prompt_template.format(code=code, version=version)

    logger.log_info(f"Analyse Ollama ({MODELE_JAVA}) en cours...")
    try:
        reponse = ollama_utils.appeler_ollama(prompt, modele=MODELE_JAVA)
        logger.log_console("\n--- RETOUR DE OLLAMA ---")
        logger.log_console(reponse)
        logger.log_console("--------------------------\n")
    except Exception as e:
        logger.log_error(f"Erreur lors de l'analyse Ollama : {e}")


def main() -> None:
    """Fonction principale."""
    if len(sys.argv) < 2:
        logger.log_warn(f"Usage: python {sys.argv[0]} VOTRE_FICHIER.java [VERSION]")
        sys.exit(1)

    fichier_cible = sys.argv[1]
    version = sys.argv[2] if len(sys.argv) > 2 else "17"
    obtenir_revue_ollama(fichier_cible, version)


if __name__ == "__main__":
    main()
