#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    ia_assistant_mrOrpr - Effectue la relecture d'une MR/PR avec l'IA choisie (Copilot, Gemini, Ollama).

DESCRIPTION
    Script Python pour relire une Merge Request (GitLab) ou Pull Request (GitHub) à l'aide d'une IA (Copilot, Gemini, Ollama).
    Analyse les changements, génère un résumé et une checklist de relecture sauvegardés en Markdown.

OPTIONS
    -u, --url URL               URL obligatoire de la MR/PR (GitLab ou GitHub)
    -ia copilot|gemini|ollama   Choix de l'IA (défaut: auto-détecté)
    --dry-run                   Simulation, affiche le prompt sans appel à l'IA
    -h, --help                  Afficher l'aide du script

EXEMPLES
    python ia_assistant_mrOrpr.py -u https://gitlab.com/repo/-/merge_requests/1 --dry-run
    python ia_assistant_mrOrpr.py -u https://github.com/user/repo/pull/456 -ia gemini

FUNCTIONS
    main() : Point d'entrée du script, gère les options et le flux principal.
"""

import argparse
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Callable

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
from python_commun.ai.copilot import envoyer_prompt_copilot
from python_commun.ai.gemini_utils import envoyer_prompt_gemini
from python_commun.ai.ia_assistant_cli_utils import detecter_ia
from python_commun.logging import logger
from python_commun.ai.ollama_utils import appeler_ollama
from python_commun.ai.prompt import charger_prompt
from python_commun.system.system import vide_repertoire
from python_commun.network.url_utils import (
    creer_url_ssh,
    rechercher_information_depuis_url,
)

HOME = Path.home()
OUT_DIR = HOME / "ia_assistant/mrOrpr"

# Mapping des IA à leurs fonctions d'envoi de prompt
IA_DISPATCHER: Dict[str, Callable[[str], str]] = {
    "copilot": envoyer_prompt_copilot,
    "gemini": envoyer_prompt_gemini,
    "ollama": lambda prompt: appeler_ollama(prompt),
}


def _parser_options() -> argparse.Namespace:
    """
    Analyse les options de la ligne de commande.

    :return: Un objet Namespace contenant les arguments parsés.
    """
    parser = argparse.ArgumentParser(description="Relecture de MR/PR via IA")
    parser.add_argument("-u", "--url", required=True, help="URL de la MR/PR à relire")
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
    ia_utilisee = args.ia or detecter_ia()
    git_token = os.environ.get("GIT_TOKEN")

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

    fichier_resume = OUT_DIR / f"resume_{numero_merge}.md"
    ecrire_resume_mr(fichier_resume, numero_merge, stats, fichier_liste_fichiers)

    fichier_checklist = OUT_DIR / f"checklist_{numero_merge}.md"
    ecrire_checklist_mr(fichier_checklist, args.url)

    # Dossier des prompts
    dossier_prompts = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "prompts")
    )

    # Construction manuelle du prompt
    prompt_template = charger_prompt("review_prompt.py", dossier_prompts)

    contenu_diff = (
        fichier_diff.read_text(encoding="utf-8") if fichier_diff.exists() else ""
    )
    contenu_resume = (
        fichier_resume.read_text(encoding="utf-8") if fichier_resume.exists() else ""
    )

    prompt = f"""
Voici une revue de code à analyser pour une Merge Request / Pull Request.

Résumé de la MR/PR :
{contenu_resume}

Diff complet :
```diff
{contenu_diff}
```

Template de base: {prompt_template}

### Instructions supplémentaires pour cette revue :
1. **Sécurité :** Identifie tout problème de sécurité potentiel (injections, exposition de secrets, mauvaises pratiques d'authentification).
2. **Risque :** Évalue le risque de fusionner ce changement sur une échelle de 1 (faible) à 10 (critique). Justifie ta note.
"""

    if args.dry_run:
        logger.log_console(f"[DRY-RUN] IA utilisée : {ia_utilisee}")
        logger.log_console(f"[DRY-RUN] Prompt qui serait généré :\n{prompt}")
        return

    # Envoi du prompt à l'IA via le dispatcher
    sender_func = IA_DISPATCHER.get(ia_utilisee)
    if not sender_func:
        logger.die(f"L'IA '{ia_utilisee}' n'est pas supportée.")

    logger.log_info(f"Revue de la MR/PR en cours avec {ia_utilisee}...")
    result = sender_func(prompt)

    md_path = OUT_DIR / f"mrOrpr_{espace_projet.replace('/', '_')}_{numero_merge}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Revue de la {plateforme} MR/PR !{numero_merge}\n\n{result}")

    logger.log_success(f"Document de revue généré : {md_path}")


if __name__ == "__main__":
    main()
