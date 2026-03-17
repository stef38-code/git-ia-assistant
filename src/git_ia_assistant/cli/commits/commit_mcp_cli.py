#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    commit_mcp_cli - Génère un message de commit en mode AGENT via MCP (Model Context Protocol).

DESCRIPTION
    Version MCP du script de commit. L'IA explore le codebase via un agent pour générer
    un message plus précis (scope, raison du changement) ou optimiser les groupes de commits.
    
    L'agent utilise le protocole MCP pour accéder aux outils d'analyse de code et de Git,
    permettant une compréhension contextuelle approfondie du projet.

OPTIONS
    --ia gemini|copilot|ollama   Choix de l'IA à utiliser (défaut: gemini)
    -f, --fichier <fichier(s)>   Liste des fichiers spécifiques à analyser
    --optimise                   Analyse et propose un regroupement en commits logiques
    --clear                      Nettoyer le répertoire de travail temporaire avant exécution
    -h, --help                   Afficher l'aide colorisée

EXEMPLES
    python commit_mcp_cli.py
    python commit_mcp_cli.py --ia copilot --optimise
    python commit_mcp_cli.py -f src/mon_fichier.py
    python commit_mcp_cli.py --clear

FUNCTIONS
    main() : Point d'entrée du script, gère la configuration de l'agent et l'orchestration MCP.
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

def determiner_ia_choisie(parser, args):
    """Détermine l'IA à utiliser (priorités) :
    1. variable d'environnement IA_SELECTED (ou IA) si valide (gemini,copilot,ollama)
    2. présence de GEMINI_API_KEY → 'gemini'
    3. présence de COPILOT_API_KEY ou GITHUB_TOKEN → 'copilot'
    4. sinon → 'ollama'
    """
    ia_defaut = parser.get_default("ia")
    ia_choisie = args.ia
    if ia_choisie == ia_defaut:
        env_ia = os.getenv("IA_SELECTED") or os.getenv("IA")
        if env_ia and env_ia.lower() in ("gemini", "copilot", "ollama"):
            return env_ia.lower()
        # Priorité aux clés API
        if os.getenv("GEMINI_API_KEY"):
            return "gemini"
        if os.getenv("COPILOT_API_KEY") or os.getenv("GITHUB_TOKEN"):
            return "copilot"
        return "ollama"
    return ia_choisie

def main():
    parser = argparse.ArgumentParser(description="Commit via Agent MCP", add_help=False)
    parser.add_argument("-h", "--help", action="store_true")
    parser.add_argument("--ia", choices=["gemini", "copilot", "ollama"], default="gemini")
    parser.add_argument("-f", "--fichier", nargs="*", help="Fichiers spécifiques")
    parser.add_argument("--dry-run", "--dryrun", action="store_true", dest="dry_run", help="Simulation : affiche l'IA choisie, vérifie rapidement les serveurs MCP et liste les fichiers")
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

    # Si mode simulation (dry-run) : afficher IA sélectionnée, tester les serveurs MCP et lister les fichiers
    if args.dry_run:
        ia_choisie = determiner_ia_choisie(parser, args)
        logger.log_info(f"[DRY-RUN] IA sélectionnée : {ia_choisie}")
        # Vérification rapide (non exhaustive) pour éviter de bloquer l'utilisateur
        # Passe une liste vide pour éviter les vérifications longues (npm list -g, pip show, etc.)
        servers_ok = McpConfigManager.verifier_installation(servers=[])
        if servers_ok:
            logger.log_info("[DRY-RUN] Vérification rapide terminée (pas d'inspection complète).")
        else:
            logger.log_warn("[DRY-RUN] Problèmes détectés lors de la vérification rapide (voir erreurs).")
        logger.log_info(f"[DRY-RUN] Fichiers pris en compte : {fichiers}")
        logger.log_info("[DRY-RUN] Pour une vérification complète, exécutez sans --dry-run.")
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
        plateforme="local",
        langage=langage,
        repo_path=repo_path
    )

    # 3. Instanciation
    ia_choisie = determiner_ia_choisie(parser, args)
    ia_type = ia_choisie + "_mcp"
    assistant = IaAssistantCommitFactory.create_commit_instance(
        ia=ia_type,
        fichiers=fichiers,
        mcp_config_path=mcp_config_path
    )

    # 4. Orchestration MCP (Démarrage avant la détection)
    try:
        assistant.demarrer_outils()

        # Préparation des fichiers (git add) - Arrivera après le démarrage MCP
        assistant.detecter_fichiers()

        # 5. Génération
        logger.log_info("🤖 L'Agent analyse vos changements...")
        
        if args.optimise:
            assistant.gerer_optimisation_mcp()
        else:
            assistant.generer_et_valider_commit_mcp()

    except Exception as e:
        err_msg = str(e).lower()
        if 'quota' in err_msg or 'exhausted' in err_msg or '429' in err_msg:
            logger.log_error(f"❌ Quota épuisé pour {ia_choisie} (Erreur 429 RESOURCE_EXHAUSTED).")
            sys.exit(1)
        else:
            logger.log_error(f"❌ Échec lors de la génération du commit {ia_choisie} : {e}")
            sys.exit(1)
    finally:
        # Arrêt systématique
        assistant.arreter_outils()

if __name__ == "__main__":
    main()
