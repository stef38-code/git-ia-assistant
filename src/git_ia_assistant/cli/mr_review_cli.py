#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    mr_review_cli - Effectue la relecture d'une MR/PR avec l'IA choisie (Copilot, Gemini, Ollama).

DESCRIPTION
    Script Python pour relire une Merge Request (GitLab) ou Pull Request (GitHub) à l'aide d'une IA.
    Analyse les changements, génère un résumé et une checklist de relecture sauvegardés en Markdown.
    
    Le script :
    - Clone ou met à jour le dépôt distant
    - Génère le diff de la MR/PR
    - Calcule les statistiques des changements
    - Génère un document de revue complet avec analyse de l'IA

OPTIONS
    -u, --url URL               URL obligatoire de la MR/PR (GitLab ou GitHub)
    -ia copilot|gemini|ollama   Choix de l'IA (défaut: auto-détecté via IA_SELECTED ou copilot)
    --dry-run                   Simulation, affiche le prompt sans appel à l'IA
    -h, --help                  Afficher l'aide du script

EXEMPLES
    git-ia-mr -u https://gitlab.com/repo/-/merge_requests/1 --dry-run
    git-ia-mr -u https://github.com/user/repo/pull/456 -ia gemini
    git-ia-mr --url https://gitlab.com/org/project/-/merge_requests/123
"""

import argparse
import os
import sys
import urllib.request
import urllib.error
import urllib3
from pathlib import Path

# Désactiver les avertissements SSL pour les serveurs avec certificats auto-signés
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Ajout du chemin racine et de la librairie commune pour permettre l'import des modules du projet
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../libs/python_commun/src")))

from python_commun.vcs.mr_utils import cloner_ou_fetch_depot, generer_diff_mr
from python_commun.vcs.diff_stats import (
    calculer_stats_mr,
    ecrire_checklist_mr,
    ecrire_resume_mr,
    extraire_fichiers_modifies,
)
from python_commun.ai.ia_assistant_cli_utils import detecter_ia
from python_commun.logging import logger
from python_commun.system.system import vide_repertoire, detect_lang_and_framework
from python_commun.network.url_utils import (
    creer_url_ssh,
    rechercher_information_depuis_url,
)
from python_commun.cli.usage import usage
from git_ia_assistant.core.definition.ia_assistant_mr_factory import IaAssistantMrFactory

HOME = Path.home()
OUT_DIR = HOME / "ia_assistant/mrOrpr"


def _parser_options() -> argparse.Namespace:
    """
    Analyse les options de la ligne de commande.

    :return: Un objet Namespace contenant les arguments parsés.
    """
    parser = argparse.ArgumentParser(
        description="Relecture de MR/PR via IA", add_help=False
    )
    parser.add_argument("-h", "--help", action="store_true", help="Afficher l'aide.")
    parser.add_argument("-u", "--url", help="URL de la MR/PR à relire")
    parser.add_argument(
        "-ia",
        choices=["copilot", "gemini", "ollama"],
        default=None,
        help="Nom de l'IA à utiliser (défaut: auto-détection)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Simulation, affiche le prompt généré"
    )
    return parser.parse_args()


def _verifier_url_existe(url: str, token: str = None) -> bool:
    """
    Vérifie si une URL est accessible, en utilisant un token d'authentification si fourni.

    :param url: L'URL à vérifier.
    :param token: Le token d'authentification (pour les dépôts privés).
    :return: True si l'URL est accessible, False sinon.
    """
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        req = urllib.request.Request(url, headers=headers, method="HEAD")
        urllib.request.urlopen(req)
        return True
    except urllib.error.HTTPError as e:
        logger.log_error(f"L'URL a retourné une erreur HTTP {e.code}: {e.reason}")
        if e.code == 401:
            logger.log_error(
                "Erreur 401 Unauthorized. Votre token (GIT_TOKEN) est peut-être invalide ou manquant."
            )
        elif e.code == 404:
            logger.log_error("Erreur 404 Not Found. Vérifiez que l'URL est correcte.")
        return False
    except Exception as e:
        logger.log_error(f"Impossible de vérifier l'URL. Erreur : {e}")
        return False


def main() -> None:
    """
    Point d'entrée principal du script.
    """
    args = _parser_options()
    
    # Gestion de l'aide
    if getattr(args, "help", False):
        usage(__file__)
        return
    
    # Vérification de l'URL obligatoire
    if not args.url:
        logger.die("L'option -u/--url est obligatoire. Utilisez -h pour l'aide.")
    
    ia_utilisee = args.ia or detecter_ia()
    git_token = os.environ.get("GIT_TOKEN")
    
    # Vérification du token pour les dépôts GitLab/GitHub
    if not args.dry_run and not git_token:
        logger.die(
            "La variable d'environnement GIT_TOKEN n'est pas définie.\n"
            "Pour GitLab: créez un Personal Access Token avec les scopes 'read_api' et 'read_repository'\n"
            "Pour GitHub: créez un Personal Access Token avec le scope 'repo'\n"
            "Puis exportez-le: export GIT_TOKEN='votre_token'"
        )

    if not args.dry_run and not _verifier_url_existe(args.url, git_token):
        logger.die("L'URL de la MR/PR est inaccessible. Arrêt du script.")

    plateforme, nom_projet, espace_projet, numero_merge = (
        rechercher_information_depuis_url(args.url)
    )
    if not all([plateforme, nom_projet, espace_projet, numero_merge]):
        logger.die("Impossible de parser les informations depuis l'URL.")

    vide_repertoire(OUT_DIR, getattr(args, "clean_outdir", True), args.dry_run)

    depot_ssh = creer_url_ssh(args.url)
    repo_local_path = OUT_DIR / depot_ssh.split(":")[-1].replace(".git", "")

    cloner_ou_fetch_depot(depot_ssh, repo_local_path, args.dry_run)

    fichier_diff = OUT_DIR / f"diff_{numero_merge}.patch"
    generer_diff_mr(
        out_dir=repo_local_path,
        numero_mr=numero_merge,
        fichier_diff=fichier_diff,
        dry_run=args.dry_run,
        plateforme=plateforme,
        espace_projet=espace_projet,
        url_mr=args.url,
        token=git_token,
    )

    fichier_liste_fichiers = OUT_DIR / f"files_{numero_merge}.txt"
    extraire_fichiers_modifies(fichier_diff, fichier_liste_fichiers)

    stats = calculer_stats_mr(fichier_diff, fichier_liste_fichiers)

    # Affichage du nombre de changements et de commits
    nb_fichiers = stats.get('fichiers_modifies', 0)
    nb_lignes_ajoutees = stats.get('additions', 0)
    nb_lignes_supprimees = stats.get('suppressions', 0)
    print(f"\nRésumé des changements :")
    print(f"- Fichiers modifiés : {nb_fichiers}")
    print(f"- Lignes ajoutées : {nb_lignes_ajoutees}")
    print(f"- Lignes supprimées : {nb_lignes_supprimees}")

    fichier_resume = OUT_DIR / f"resume_{numero_merge}.md"
    ecrire_resume_mr(fichier_resume, numero_merge, stats, fichier_liste_fichiers)

    fichier_checklist = OUT_DIR / f"checklist_{numero_merge}.md"
    ecrire_checklist_mr(fichier_checklist, args.url)

    # Détection du langage et framework du projet
    langage_framework = detect_lang_and_framework(repo_local_path)
    logger.log_info(f"Langage/Framework détecté : {langage_framework}")

    # Utilisation du pattern Factory pour instancier la classe IA appropriée
    ia_class = IaAssistantMrFactory.get_mr_class(ia_utilisee)
    ia_instance = ia_class(
        url_mr=args.url,
        plateforme=plateforme,
        numero_mr=numero_merge,
        out_dir=OUT_DIR,
        dry_run=args.dry_run,
        langage=langage_framework,
    )

    # Génération de la revue via l'IA
    result = ia_instance.generer_revue_mr(fichier_diff, fichier_resume)

    # En mode dry-run, la méthode retourne None après affichage
    if args.dry_run:
        return

    # Sauvegarde du résultat
    if result:
        md_path = OUT_DIR / f"mrOrpr_{espace_projet.replace('/', '_')}_{numero_merge}.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# Revue de la {plateforme} MR/PR !{numero_merge}\n\n{result}")
        logger.log_success(f"Document de revue généré : {md_path}")
    else:
        logger.log_error("Échec de la génération de la revue.")


if __name__ == "__main__":
    main()
