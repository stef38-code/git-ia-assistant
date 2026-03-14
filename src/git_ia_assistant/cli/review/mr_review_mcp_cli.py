#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    mr_review_mcp_cli - Revue de MR/PR en mode AGENT via serveurs MCP.

DESCRIPTION
    Cette version "MCP" du script de revue délègue l'exploration du code à l'IA.
    L'IA utilise des outils (git, filesystem, ripgrep) pour analyser les changements.
    
    Avantages :
    - Moins de tokens consommés (pas d'envoi du diff complet)
    - Meilleure analyse (l'IA peut lire les fichiers complets)
    - Plus rapide (pas de génération de patch locale)

OPTIONS
    -u, --url URL               URL de la MR/PR (OBLIGATOIRE)
    -ia gemini|copilot          Choix de l'IA (défaut: gemini car mieux adapté au MCP)
    --publier                   Publier le rapport en commentaire
    -h, --help                  Afficher l'aide
"""

import argparse
import os
import sys
from pathlib import Path

# Ajout des chemins imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../libs/python_commun/src")))

from python_commun.logging import logger
from python_commun.system.system import vide_repertoire, detect_lang_and_framework
from python_commun.network.url_utils import rechercher_information_depuis_url
from python_commun.cli.usage import usage
from git_ia_assistant.core.definition.ia_assistant_mr_factory import IaAssistantMrFactory
from git_ia_assistant.cli.mcp.mcp_config_manager import McpConfigManager

HOME = Path.home()
OUT_DIR = HOME / "ia_assistant/mr_mcp"

def main():
    parser = argparse.ArgumentParser(description="Revue MR via Agent MCP", add_help=False)
    parser.add_argument("-h", "--help", action="store_true")
    parser.add_argument("-u", "--url")
    parser.add_argument("-ia", choices=["gemini", "copilot"], default="gemini")
    parser.add_argument("--publier", action="store_true")
    args = parser.parse_args()

    if args.help:
        usage(__file__)
        return

    if not args.url:
        logger.die("L'URL (-u) est obligatoire.")

    git_token = os.environ.get("GIT_TOKEN")
    if not git_token:
        logger.die("GIT_TOKEN manquant dans l'environnement.")

    # 1. Analyse de l'URL
    plateforme, nom_projet, espace_projet, numero_mr = rechercher_information_depuis_url(args.url)
    if not all([plateforme, nom_projet, espace_projet, numero_mr]):
        logger.die("URL invalide.")

    logger.log_info(f"🚀 Démarrage de la revue MCP pour {plateforme} !{numero_mr}")

    # 2. Préparation du répertoire de travail (léger)
    vide_repertoire(OUT_DIR, True, False)
    
    # On a besoin du chemin local pour le serveur MCP filesystem
    # Note: Dans une version future, on pourrait même éviter le clone local si le serveur MCP Git 
    # sait parler aux APIs distantes, mais pour l'instant on suppose un repo local.
    repo_path = Path(os.getcwd()) # Par défaut, on suppose qu'on est dans le repo ou on l'indique

    # 3. Configuration des serveurs MCP
    langage = detect_lang_and_framework(repo_path)
    logger.log_info(f"🛠️  Configuration des outils pour : {langage}")
    
    mcp_config_path = McpConfigManager.generer_config(
        out_dir=OUT_DIR,
        plateforme=plateforme,
        langage=langage,
        token=git_token,
        repo_path=repo_path
    )

    if not mcp_config_path:
        logger.die("Impossible de générer la configuration MCP.")

    # 4. Instanciation de l'IA (Version MCP)
    # On utilise la factory existante mais on va s'assurer que l'instance sait qu'elle est en mode MCP
    ia_instance = IaAssistantMrFactory.create_mr_instance(
        ia=args.ia,
        url_mr=args.url,
        plateforme=plateforme,
        numero_mr=numero_mr,
        out_dir=OUT_DIR,
        langage=langage,
        mcp_config_path=mcp_config_path,
        # On passe un flag spécifique pour indiquer le mode Agent si nécessaire
    )

    # 5. Lancement de la revue Agentique
    # En mode MCP, on ne passe pas de fichiers diff/resume car l'IA les récupérera elle-même
    logger.log_info("🤖 L'Agent IA explore le codebase...")
    
    # On appelle une méthode spécifique au mode MCP si elle existe, 
    # sinon on adapte generer_revue_mr pour qu'elle comprenne le mode MCP
    result = ia_instance.generer_revue_mr(diff_path=None, resume_path=None)

    if result:
        output_file = OUT_DIR / f"revue_mcp_{numero_mr}.md"
        output_file.write_text(result, encoding="utf-8")
        logger.log_success(f"✅ Revue terminée ! Rapport : {output_file}")
        
        if args.publier:
            # Logique de publication (réutilisée depuis python_commun)
            from python_commun.vcs.mr_utils import publier_commentaire_mr
            publier_commentaire_mr(
                numero_mr=numero_mr,
                commentaire=f"# 🤖 Revue Agentique (MCP)\n\n{result}",
                plateforme=plateforme,
                espace_projet=espace_projet,
                url_mr=args.url,
                token=git_token
            )
    else:
        logger.log_error("❌ L'Agent n'a pas pu générer la revue.")

if __name__ == "__main__":
    main()
