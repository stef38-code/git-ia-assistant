#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    ollama_angular_review - Effectue une revue de code Angular avec Ollama.

DESCRIPTION
    Ce script envoie le code TypeScript/HTML Angular à Ollama pour obtenir
    une analyse sur les bugs potentiels, les optimisations et le respect
    des bonnes pratiques. Il sert de point d'entrée pour la revue de code
    Angular via l'IA Ollama.

SYNOPSIS
    python ollama_angular_review.py VOTRE_FICHIER.ts [VERSION]

FUNCTIONS
    obtenir_revue_ollama(chemin_fichier: str, version: str = "15") -> None
        Envoie le code à Ollama pour une analyse technique et affiche le résultat.
    main() -> None
        Fonction principale du script, gère les arguments et l'exécution de la revue.

DATA
    MODELE_ANGULAR: str
        Nom du modèle Ollama par défaut utilisé pour la revue Angular.
"""

import sys

from python_commun.logging.logger import logger
from git_ia_assistant.ia.ollama import ollama_utils

# Modèle par défaut pour la revue Angular
MODELE_ANGULAR = "codeqwen"


def obtenir_revue_ollama(chemin_fichier: str, version: str = "15") -> None:
    """
    Envoie le code à Ollama pour une analyse technique.

    :param chemin_fichier: Le chemin vers le fichier à analyser.
    :param version: La version d'Angular utilisée.
    """
    try:
        with open(chemin_fichier, "r", encoding="utf-8") as f:
            code = f.read()
    except FileNotFoundError:
        logger.die(f"Le fichier {chemin_fichier} n'a pas été trouvé.")

    prompt_template = ollama_utils.charger_prompt("angular_review_prompt.md")
    prompt = prompt_template.format(code=code, version=version)

    logger.log_info(f"Analyse Ollama ({MODELE_ANGULAR}) en cours...")
    try:
        reponse = ollama_utils.appeler_ollama(prompt, modele=MODELE_ANGULAR)
        logger.log_console("\n--- RETOUR DE OLLAMA ---")
        logger.log_console(reponse)
        logger.log_console("--------------------------\n")
    except Exception as e:
        logger.log_error(f"Erreur lors de l'analyse Ollama : {e}")


def main() -> None:
    """Fonction principale."""
    if len(sys.argv) < 2:
        logger.log_warn(f"Usage: python {sys.argv[0]} VOTRE_FICHIER.ts [VERSION]")
        sys.exit(1)

    fichier_cible = sys.argv[1]
    version = sys.argv[2] if len(sys.argv) > 2 else "15"
    obtenir_revue_ollama(fichier_cible, version)


if __name__ == "__main__":
    main()
