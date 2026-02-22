#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    ia_assistant_doc - Génère la documentation d'un fichier avec l'IA choisie (Copilot, Gemini, Ollama).

DESCRIPTION
    Script Python pour générer la documentation d'un fichier source à l'aide d'une IA (Copilot, Gemini, Ollama).
    Permet de spécifier le format de sortie et la langue de la documentation.

OPTIONS
    fichier                     Fichier source à documenter (obligatoire)
    -ia copilot|gemini|ollama   Choix de l'IA (défaut: auto-détecté)
    -f, --format FORMAT         Format de doc (ex: Markdown, Javadoc, Docstrings)
    -l, --langue LANGUE         Langue de la doc (défaut: Français)
    --dry-run                   Simulation, affiche le prompt sans appel à l'IA
    -h, --help                  Afficher l'aide du script

EXEMPLES
    python ia_assistant_doc.py mon_fichier.py -ia gemini
    python ia_assistant_doc.py src/main.java --format Javadoc
    python ia_assistant_doc.py script.py --dry-run

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
from git_ia_assistant.core.definition.ia_assistant_doc_factory import IaAssistantDocFactory

def _parser_options() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Génération de documentation IA")
    parser.add_argument("fichier", help="Fichier à documenter")
    parser.add_argument("-ia", choices=["copilot", "gemini", "ollama"], help="IA à utiliser")
    parser.add_argument("-f", "--format", help="Format de doc (ex: Markdown, Javadoc, Docstrings)")
    parser.add_argument("-l", "--langue", default="Français", help="Langue de la doc (défaut: Français)")
    parser.add_argument("--dry-run", action="store_true", help="Afficher le prompt généré")
    return parser.parse_args()

def main() -> None:
    args = _parser_options()
    
    if not os.path.exists(args.fichier):
        logger.die(f"Le fichier {args.fichier} n'existe pas.")

    nom_ia = args.ia or detecter_ia()
    
    try:
        doc_cls = IaAssistantDocFactory.get_doc_class(nom_ia)
        assistant = doc_cls(args.fichier, doc_format=args.format, langue=args.langue)
        
        prompt = assistant.generer_prompt()
        
        if args.dry_run:
            logger.log_console(f"[DRY-RUN] IA utilisée : {nom_ia}")
            logger.log_console(f"[DRY-RUN] Prompt qui serait envoyé :\n{prompt}")
            return

        logger.log_info(f"Génération de la documentation pour {args.fichier} avec {nom_ia}...")
        doc_generee = assistant.generer_doc()
        
        logger.log_console("\n" + "=" * 30 + f" DOCUMENTATION GÉNÉRÉE POUR : {args.fichier} " + "=" * 30)
        logger.log_console(doc_generee)
        logger.log_console("=" * 80)

    except Exception as e:
        logger.die(f"Erreur : {e}")

if __name__ == "__main__":
    main()
