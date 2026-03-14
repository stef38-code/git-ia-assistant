#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    commit_mcp_cli - Génère un message de commit en mode AGENT via MCP.

DESCRIPTION
    Version MCP du script de commit. L'IA explore le codebase pour générer
    un message plus précis (scope, pourquoi) ou optimiser les groupes de commits.
"""

import argparse
import os
import sys
from pathlib import Path

# Chemins
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../libs/python_commun/src")))

from python_commun.logging import logger
from python_commun.system.system import detect_lang_and_framework
from python_commun.git.git_core import liste_fichier_non_suivis_et_modifies
from python_commun.cli.usage import usage
from git_ia_assistant.cli.mcp.mcp_config_manager import McpConfigManager
from git_ia_assistant.core.definition.ia_assistant_commit_factory import IaAssistantCommitFactory

HOME = Path.home()
OUT_DIR = HOME / "ia_assistant/commits_mcp"

def main():
    parser = argparse.ArgumentParser(description="Commit via Agent MCP", add_help=False)
    parser.add_argument("-h", "--help", action="store_true")
    parser.add_argument("--ia", choices=["gemini", "copilot", "ollama"], default="gemini")
    parser.add_argument("-f", "--fichier", nargs="*", help="Fichiers spécifiques")
    parser.add_argument("--optimise", action="store_true", help="Proposer des commits logiques")
    parser.add_argument("--clear", action="store_true", help="Nettoyer le répertoire de travail")
    args = parser.parse_args()

    if args.help:
        usage(__file__)
        return

    # 1. Détection des fichiers
    fichiers = args.fichier or liste_fichier_non_suivis_et_modifies()
    if not fichiers:
        logger.log_warn("Aucun changement détecté.")
        return

    # 2. Configuration MCP
    repo_path = Path(os.getcwd())
    langage = detect_lang_and_framework(repo_path)
    
    if args.clear:
        from python_commun.system.system import vide_repertoire
        vide_repertoire(OUT_DIR, True, False)

    logger.log_info(f"🚀 Initialisation de l'Agent Commit (MCP) pour : {langage}")
    
    mcp_config_path = McpConfigManager.generer_config(
        out_dir=OUT_DIR,
        plateforme="local", # Pour le commit, on se concentre sur les outils locaux
        langage=langage,
        repo_path=repo_path
    )

    # 3. Instanciation de l'IA (Version MCP)
    ia_type = args.ia + "_mcp"
    assistant = IaAssistantCommitFactory.create_commit_instance(
        ia=ia_type,
        fichiers=fichiers,
        mcp_config_path=mcp_config_path
    )

    # Préparation des fichiers (git add) et affichage stats
    assistant.detecter_fichiers()

    # 4. Génération
    logger.log_info("🤖 L'Agent analyse vos changements...")
    
    result = None
    try:
        if args.optimise:
            assistant.gerer_optimisation_mcp()
        else:
            assistant.generer_et_valider_commit_mcp()
    except Exception as e:
        err_msg = str(e).lower()
        if 'quota' in err_msg or 'exhausted' in err_msg or '429' in err_msg:
            logger.log_error(f"❌ Quota épuisé pour {args.ia} (Erreur 429 RESOURCE_EXHAUSTED).")
            logger.log_info("")
            logger.log_info("💡 Solutions possibles :")
            logger.log_info("   1. Attendre quelques minutes avant de réessayer.")
            logger.log_info("   2. Utiliser une autre IA (ex: --ia copilot).")
            logger.log_info("   3. Passer sur une IA locale (ex: --ia ollama) pour éviter les quotas distants.")
            sys.exit(1)
        else:
            logger.log_error(f"❌ Échec lors de la génération du commit {args.ia} : {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
