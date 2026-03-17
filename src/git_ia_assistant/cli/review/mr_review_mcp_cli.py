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
import urllib3

# Désactiver les avertissements SSL pour les serveurs avec certificats auto-signés
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Ajout des chemins imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../libs/python_commun/src")))

from python_commun.logging import logger
from python_commun.system.system import vide_repertoire, detect_lang_and_framework
from python_commun.network.url_utils import rechercher_information_depuis_url
from python_commun.cli.usage import usage
from git_ia_assistant.core.definition.ia_assistant_mr_factory import IaAssistantMrFactory
from git_ia_assistant.cli.mcp.mcp_config_manager import McpConfigManager
from python_commun.ai.mcp_client_manager import McpClientManager

HOME = Path.home()
OUT_DIR = HOME / "ia_assistant/mr_mcp"

def determiner_ia_choisie(parser, args):
    ia_defaut = parser.get_default("ia")
    ia_choisie = args.ia
    if ia_choisie == ia_defaut:
        env_ia = os.getenv("IA_SELECTED") or os.getenv("IA")
        if env_ia and env_ia.lower() in ("gemini", "copilot", "ollama"):
            return env_ia.lower()
        if os.getenv("GEMINI_API_KEY"):
            return "gemini"
        if os.getenv("COPILOT_API_KEY") or os.getenv("GITHUB_TOKEN"):
            return "copilot"
        return "ollama"
    return ia_choisie


def main():
    parser = argparse.ArgumentParser(description="Revue MR via Agent MCP", add_help=False)
    parser.add_argument("-h", "--help", action="store_true")
    parser.add_argument("-u", "--url")
    parser.add_argument("-ia", choices=["gemini", "copilot", "ollama"], default="gemini")
    parser.add_argument("--dry-run", "--dryrun", action="store_true", dest="dry_run", help="Simulation : affiche l'IA choisie, vérifie rapidement les serveurs MCP et affiche la MR à analyser")
    parser.add_argument("--publier", action="store_true")
    parser.add_argument("--clear", action="store_true", help="Vider le répertoire de sortie classique (mrOrpr)")
    args = parser.parse_args()

    if args.help:
        usage(__file__)
        return

    if not args.url:
        logger.die("L'URL (-u) est obligatoire.")

    # Déterminer l'IA choisie (avec priorités similaires à commit_mcp_cli)
    ia_choisie = determiner_ia_choisie(parser, args)
    ia_type = ia_choisie + "_mcp"

    # Priorité aux tokens standardisés (GIT/GITHUB/GITLAB)
    git_token = os.environ.get("GIT_TOKEN") or os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN") or os.environ.get("GITLAB_PRIVATE_TOKEN")

    # 1. Analyse de l'URL
    plateforme, nom_projet, espace_projet, numero_mr = rechercher_information_depuis_url(args.url)
    if not all([plateforme, nom_projet, espace_projet, numero_mr]):
        logger.die("URL invalide.")

    logger.log_info(f"🚀 Démarrage de la revue MCP pour {plateforme} !{numero_mr}")

    # 2. Vérification rapide si dry-run
    if args.dry_run:
        logger.log_info(f"[DRY-RUN] IA sélectionnée : {ia_choisie}")
        servers_ok = McpConfigManager.verifier_installation(servers=[])
        if servers_ok:
            logger.log_info("[DRY-RUN] Vérification rapide terminée (pas d'inspection complète).")
        else:
            logger.log_warn("[DRY-RUN] Problèmes détectés lors de la vérification rapide (voir erreurs).")
        logger.log_info(f"[DRY-RUN] MR à analyser : {args.url}")
        logger.log_info("[DRY-RUN] Pour une vérification complète, exécutez sans --dry-run.")
        return

    if not git_token:
        # Message plus explicite pour indiquer quel token est attendu selon la plateforme
        if plateforme == 'gitlab':
            logger.die("GITLAB_PRIVATE_TOKEN (ou GIT_TOKEN) manquant dans l'environnement.")
        elif plateforme == 'github':
            logger.die("GITHUB_PERSONAL_ACCESS_TOKEN (ou GIT_TOKEN) manquant dans l'environnement.")
        else:
            logger.die("GIT token manquant dans l'environnement (export GIT_TOKEN).")

    # 2. Gestion du nettoyage si demandé
    if args.clear:
        DIR_A_VIDER = Path.home() / "ia_assistant/mrOrpr"
        vide_repertoire(DIR_A_VIDER, True, False)
    
    # Vider le répertoire MCP pour éviter les artefacts d'exécutions précédentes
    from python_commun.system.system import vide_repertoire
    try:
        vide_repertoire(OUT_DIR, True, args.dry_run)
    except Exception:
        # Si l'effacement échoue, poursuivre mais avertir
        logger.log_warn(f"Impossible de vider {OUT_DIR} avant exécution. Les fichiers existants peuvent influencer la revue.")

    # Préparer le dépôt local (cloner/fetch) pour permettre au serveur MCP 'filesystem' et aux prompts
    from python_commun.vcs.mr_utils import cloner_ou_fetch_depot, generer_diff_mr
    from python_commun.vcs.diff_stats import extraire_fichiers_modifies, calculer_stats_mr, ecrire_resume_mr, ecrire_checklist_mr
    from python_commun.network.url_utils import creer_url_ssh

    depot_ssh = creer_url_ssh(args.url)
    # cloner_ou_fetch_depot construit le chemin final lui-même, on passe juste le répertoire de base
    cloner_ou_fetch_depot(depot_ssh, OUT_DIR, args.dry_run)
    repo_local_path = OUT_DIR / depot_ssh.split(":")[-1].replace(".git", "")

    # Générer un diff minimal pour la MR afin de produire le resume et la liste de fichiers
    fichier_diff = OUT_DIR / f"diff_{numero_mr}.patch"
    generer_diff_mr(
        out_dir=repo_local_path,
        numero_mr=numero_mr,
        fichier_diff=fichier_diff,
        dry_run=args.dry_run,
        plateforme=plateforme,
        espace_projet=espace_projet,
        url_mr=args.url,
        token=git_token,
    )

    fichier_liste_fichiers = OUT_DIR / f"files_{numero_mr}.txt"
    extraire_fichiers_modifies(fichier_diff, fichier_liste_fichiers)

    stats = calculer_stats_mr(fichier_diff, fichier_liste_fichiers)

    # Écrire le résumé et la checklist pour que les prompts MCP puissent les retrouver
    fichier_resume = OUT_DIR / f"resume_{numero_mr}.md"
    ecrire_resume_mr(fichier_resume, numero_mr, stats, fichier_liste_fichiers)

    fichier_checklist = OUT_DIR / f"checklist_{numero_mr}.md"
    ecrire_checklist_mr(fichier_checklist, args.url)

    # On a besoin du chemin local pour le serveur MCP filesystem
    repo_path = repo_local_path

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

    # Afficher l'initialisation de l'agent (aligné sur commit_mcp_cli)
    logger.log_info(f"🚀 Initialisation de l'Agent Revue (MCP) pour : {langage}")

    # Afficher IA choisie et modèle si disponible
    model_info = ""
    if ia_choisie == "gemini":
        model_info = os.getenv("GEMINI_MODEL") or "gemini-2.5-flash"
    elif ia_choisie == "ollama":
        model_info = os.getenv("OLLAMA_MODEL") or "(local ollama)"
    elif ia_choisie == "copilot":
        model_info = os.getenv("COPILOT_MODEL") or "(copilot)"
    logger.log_info(f"ℹ INFO:  IA sélectionnée : {ia_choisie} {('- model: ' + model_info) if model_info else ''}")

    # Instanciation de l'IA (Version MCP)
    ia_instance = IaAssistantMrFactory.create_mr_instance(
        ia=ia_type,
        url_mr=args.url,
        plateforme=plateforme,
        numero_mr=numero_mr,
        out_dir=OUT_DIR,
        langage=langage,
        mcp_config_path=mcp_config_path,
    )

    # Démarrage des serveurs MCP via McpClientManager pour afficher immédiatement
    # les logs de démarrage (nombre d'outils chargés, erreurs de TLS, etc.).
    mcp_manager = None
    try:
        mcp_manager = McpClientManager(mcp_config_path)
        mcp_manager.demarrer_serveurs()
    except Exception as e:
        logger.log_warn(f"Erreur lors du démarrage des serveurs MCP : {e}")

    # Fournir le manager à l'instance IA pour réutilisation
    if mcp_manager:
        ia_instance.mcp_manager = mcp_manager

    # Lancement de la revue Agentique
    logger.log_info("🤖 Lancement de la revue Agentique...")

    try:
        result = ia_instance.generer_revue_mr(diff_path=None, resume_path=None)

        if result:
            # Enregistrer le rapport avec un nom canonique pour les revues MCP
            rapport_file = OUT_DIR / f"rapport_mr{numero_mr}.md"
            rapport_file.write_text(result, encoding="utf-8")

            # Egalement exporter dans le format historique mrOrpr_{project}_{N}.md pour compatibilité
            safe_project = espace_projet.replace('/', '_')
            historic_file = OUT_DIR / f"mrOrpr_{safe_project}_{numero_mr}.md"
            try:
                with open(historic_file, 'w', encoding='utf-8') as hf:
                    hf.write(f"# Revue de la {plateforme} MR/PR !{numero_mr}\n\n{result}")
            except Exception:
                # Si l'écriture échoue on continue, le fichier principal est créé
                pass

            logger.log_success(f"✅ Revue terminée ! Rapport : {rapport_file}")

            if args.publier:
                from python_commun.vcs.mr_utils import publier_commentaire_mr
                publier_commentaire_mr(
                    numero_mr=numero_mr,
                    commentaire=f"# 🤖 Revue Agentique (MCP)\n\n{result}",
                    plateforme=plateforme,
                    espace_projet=espace_projet,
                    url_mr=args.url,
                    token=git_token,
                )
        else:
            logger.log_error("❌ L'Agent n'a pas pu générer la revue.")

    except Exception as e:
        err_msg = str(e).lower()
        if 'quota' in err_msg or 'exhausted' in err_msg or '429' in err_msg:
            logger.log_error(f"❌ Quota épuisé pour {ia_choisie} (Erreur 429 RESOURCE_EXHAUSTED).")
            logger.log_info("")
            logger.log_info("💡 Solutions possibles :")
            logger.log_info("   1. Attendre quelques minutes avant de réessayer.")
            logger.log_info("   2. Utiliser une autre IA (ex: -ia copilot).")
            logger.log_info("   3. Passer sur une IA locale (ex: -ia ollama) pour éviter les quotas distants.")
            sys.exit(1)
        else:
            logger.log_error(f"❌ Échec lors de la génération de la revue {ia_choisie} : {e}")
            sys.exit(1)

    finally:
        # Arrêt systématique des serveurs MCP
        if mcp_manager:
            try:
                mcp_manager.arreter_serveurs()
            except Exception:
                pass
        logger.log_info("🔌 Arrêt des serveurs MCP terminé.")



if __name__ == "__main__":
    main()
