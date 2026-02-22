#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    ia_assistant_refacto - Script principal pour la refactorisation de code via IA.
"""

import argparse
import os
import sys

# Ajout des chemins nécessaires
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../libs/python_commun/src")))

from python_commun.ai.ia_assistant_cli_utils import detecter_ia
from python_commun.logging import logger
from git_ia_assistant.core.definition.ia_assistant_refacto_factory import IaAssistantRefactoFactory

def _parser_options() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Refactorisation de code IA")
    parser.add_argument("fichier", help="Fichier à refactoriser")
    parser.add_argument("-ia", choices=["copilot", "gemini", "ollama"], help="IA à utiliser")
    parser.add_argument("-v", "--version", help="Version cible du langage (ex: 3.12, 17)")
    parser.add_argument("--dry-run", action="store_true", help="Afficher le prompt généré")
    return parser.parse_args()

def main() -> None:
    args = _parser_options()
    
    if not os.path.exists(args.fichier):
        logger.die(f"Le fichier {args.fichier} n'existe pas.")

    nom_ia = args.ia or detecter_ia()
    
    try:
        refacto_cls = IaAssistantRefactoFactory.get_refacto_class(nom_ia)
        assistant = refacto_cls(args.fichier, version=args.version)
        
        prompt = assistant.generer_prompt()
        
        if args.dry_run:
            logger.log_console(f"[DRY-RUN] IA utilisée : {nom_ia}")
            logger.log_console(f"[DRY-RUN] Prompt qui serait envoyé :\n{prompt}")
            return

        logger.log_info(f"Refactorisation du fichier {args.fichier} avec {nom_ia}...")
        refacto_genere = assistant.refactoriser_code()
        
        logger.log_console("\n" + "=" * 30 + f" RÉFÉRENTIEL REFACTORISÉ : {args.fichier} " + "=" * 30)
        logger.log_console(refacto_genere)
        logger.log_console("=" * 80)

    except Exception as e:
        logger.die(f"Erreur : {e}")

if __name__ == "__main__":
    main()
