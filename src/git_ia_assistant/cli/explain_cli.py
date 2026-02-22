#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    ia_assistant_explain - Analyse et explique le code source avec l'IA choisie (Copilot, Gemini, Ollama).

DESCRIPTION
    Script Python pour obtenir des explications détaillées sur un fichier source à l'aide d'une IA (Copilot, Gemini, Ollama).
    Analyse la structure et le fonctionnement du code pour faciliter sa compréhension.

OPTIONS
    fichier                     Fichier source à expliquer (obligatoire)
    -ia copilot|gemini|ollama   Choix de l'IA (défaut: auto-détecté)
    --dry-run                   Simulation, affiche le prompt sans appel à l'IA
    -h, --help                  Afficher l'aide du script

EXEMPLES
    python ia_assistant_explain.py mon_script.py
    python ia_assistant_explain.py src/utils.py -ia gemini
    python ia_assistant_explain.py code.java --dry-run

FUNCTIONS
    main() : Point d'entrée du script, gère les options et le flux principal.
"""

import argparse
import os
import sys

# Ajout des chemins nécessaires
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../libs/python_commun/src")))

from python_commun.ai.ia_assistant_cli_utils import detecter_ia
from python_commun.logging import logger
from git_ia_assistant.core.definition.ia_assistant_explain_factory import IaAssistantExplainFactory

def _parser_options() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Explication de code IA")
    parser.add_argument("fichier", help="Fichier à expliquer")
    parser.add_argument("-ia", choices=["copilot", "gemini", "ollama"], help="IA à utiliser")
    parser.add_argument("--dry-run", action="store_true", help="Afficher le prompt généré")
    return parser.parse_args()

def main() -> None:
    args = _parser_options()
    
    if not os.path.exists(args.fichier):
        logger.die(f"Le fichier {args.fichier} n'existe pas.")

    nom_ia = args.ia or detecter_ia()
    
    try:
        explain_cls = IaAssistantExplainFactory.get_explain_class(nom_ia)
        assistant = explain_cls(args.fichier)
        
        prompt = assistant.generer_prompt()
        
        if args.dry_run:
            logger.log_console(f"[DRY-RUN] IA utilisée : {nom_ia}")
            logger.log_console(f"[DRY-RUN] Prompt qui serait envoyé :\n{prompt}")
            return

        logger.log_info(f"Analyse du fichier {args.fichier} avec {nom_ia}...")
        explication = assistant.expliquer_code()
        
        logger.log_console("\n" + "=" * 30 + f" EXPLICATION DE : {args.fichier} " + "=" * 30)
        logger.log_console(explication)
        logger.log_console("=" * 80)

    except Exception as e:
        logger.die(f"Erreur : {e}")

if __name__ == "__main__":
    main()
