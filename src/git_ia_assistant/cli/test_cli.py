#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    ia_assistant_test - Script principal pour la génération de tests via IA.
"""

import argparse
import os
import sys

# Ajout des chemins nécessaires
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../libs/python_commun/src")))

from python_commun.ai.ia_assistant_cli_utils import detecter_ia
from python_commun.logging import logger
from git_ia_assistant.core.definition.ia_assistant_test_factory import IaAssistantTestFactory

def _parser_options() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Génération de tests IA")
    parser.add_argument("fichier", help="Fichier source pour lequel générer des tests")
    parser.add_argument("-ia", choices=["copilot", "gemini", "ollama"], help="IA à utiliser")
    parser.add_argument("-f", "--framework", help="Framework de test (ex: PyTest, JUnit, Playwright, Vitest)")
    parser.add_argument("-v", "--version", default="latest", help="Version du framework (défaut: latest)")
    parser.add_argument("-t", "--type", choices=["unit", "integration", "e2e"], default="unit", help="Type de test (unit, integration, e2e)")
    parser.add_argument("--dry-run", action="store_true", help="Afficher le prompt généré")
    return parser.parse_args()

def main() -> None:
    args = _parser_options()
    
    if not os.path.exists(args.fichier):
        logger.die(f"Le fichier {args.fichier} n'existe pas.")

    nom_ia = args.ia or detecter_ia()
    
    try:
        test_cls = IaAssistantTestFactory.get_test_class(nom_ia)
        assistant = test_cls(args.fichier, test_framework=args.framework, test_type=args.type)
        
        prompt = assistant.generer_prompt(framework_version=args.version)
        
        if args.dry_run:
            logger.log_console(f"[DRY-RUN] IA utilisée : {nom_ia}")
            logger.log_console(f"[DRY-RUN] Prompt qui serait envoyé :\n{prompt}")
            return

        logger.log_info(f"Génération des tests pour {args.fichier} avec {nom_ia}...")
        tests_generes = assistant.generer_tests(framework_version=args.version)
        
        logger.log_console("\n" + "=" * 30 + f" TESTS GÉNÉRÉS POUR : {args.fichier} " + "=" * 30)
        logger.log_console(tests_generes)
        logger.log_console("=" * 80)

    except Exception as e:
        logger.die(f"Erreur : {e}")

if __name__ == "__main__":
    main()
