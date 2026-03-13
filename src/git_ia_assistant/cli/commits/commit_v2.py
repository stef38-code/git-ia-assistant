#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    commit_v2 - Assistant de génération et gestion de commits (version 2)

DESCRIPTION
    CLI pour générer un message de commit assisté par IA et exécuter la feuille de route
    de publication : génération du message → incrémentation de version → mise à jour
    du CHANGELOG → commit → push.

    Ce script reprend les comportements de commit_cli.py en les explicitant et en
    rendant visibles les étapes de la feuille de route.

OPTIONS
    -h, --help                  Afficher l'aide
    --dry-run                   Simulation (ne modifie rien, n'appelle pas l'IA)
    --ia copilot|gemini|ollama   Choix de l'IA (défaut: copilot)
    -f, --fichier <fichier(s)>  Liste des fichiers à analyser (défaut: détecte les modifs git)
    --optimise                  Optimise en regroupant en commits logiques
    --partiel                   Permet le découpage des fichiers (git add -p)

ENVIRONMENT
    IA_SELECTED                 Choix de l'IA si --ia absent

EXAMPLES
    python commit_v2.py --dry-run
    python commit_v2.py --ia gemini -f src/foo.py

FUNCTIONS
    main() : point d'entrée

"""

import argparse
import os
import sys
from typing import List, Set

# Permet d'importer la librairie commune et le projet
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../libs/python_commun/src")))

from python_commun.logging import logger
from python_commun.cli.usage import usage
from python_commun.git.git_core import (
    liste_fichier_non_suivis_et_modifies,
    editer_texte_avec_editeur,
    ajouter_fichiers_interactif,
    reinitialiser_index,
    ajouter_fichiers_a_index,
    a_des_changements_indexes,
    effectuer_commit_avec_message,
    pousser_vers_distant,
)

from git_ia_assistant.core.definition.ia_assistant_commit_factory import (
    IaAssistantCommitFactory,
)


def _parser_options() -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False, description="Assistant commit v2")
    parser.add_argument("--ia", choices=["copilot", "gemini", "ollama"], default="copilot", help="IA à utiliser (défaut: copilot)")
    parser.add_argument("-f", "--fichier", nargs="*", help="Nom(s) de fichier à analyser")
    parser.add_argument("--dry-run", action="store_true", help="Simulation sans appel à l'IA")
    parser.add_argument("--optimise", action="store_true", help="Optimise en groupant en commits logiques")
    parser.add_argument("--partiel", action="store_true", help="Permet de séparer un fichier en plusieurs commits (nécessite --optimise)")
    parser.add_argument("-h", "--help", action="store_true", help="Afficher l'aide")
    return parser.parse_args()


def afficher_simulation(ia_choisie: str, fichiers: List[str]) -> None:
    """Affiche un aperçu (dry-run) des opérations sans rien modifier."""
    logger.log_info(f"[DRY-RUN] IA: {ia_choisie}")
    logger.log_info(f"[DRY-RUN] Fichiers: {fichiers}")

    commit_classe = IaAssistantCommitFactory.get_commit_class(ia_choisie)
    assistant = commit_classe(fichiers)
    assistant.detecter_fichiers()

    diff = assistant.get_diff()
    logger.log_console(f"[DRY-RUN] Diff simulé:\n{diff}")


def _demander_confirmation(message: str, valeur_defaut: str = "y") -> str:
    invite = f"{message} [défaut: {valeur_defaut}] : "
    rep = input(invite).strip().lower()
    return rep if rep else valeur_defaut


def main() -> None:
    arguments = _parser_options()
    if getattr(arguments, "help", False):
        usage(__file__)
        return

    # Choix de l'IA en respectant IA_SELECTED
    ia_valides = {"copilot", "gemini", "ollama"}
    ia_env = os.getenv("IA_SELECTED")
    ia_option_presente = "--ia" in sys.argv
    if not ia_option_presente and ia_env in ia_valides:
        ia_choisie = ia_env
    else:
        ia_choisie = arguments.ia

    fichiers_a_analyser = arguments.fichier or []
    if not fichiers_a_analyser:
        fichiers_a_analyser = liste_fichier_non_suivis_et_modifies()

    if not fichiers_a_analyser:
        logger.log_warn("Aucun fichier à analyser. Fin.")
        return

    # Afficher la feuille de route (étapes) explicitement
    feuille_route = [
        "Génération du message de commit",
        "Incrémentation de la version",
        "Mise à jour du CHANGELOG",
        "Commit des fichiers (code + version + CHANGELOG)",
        "Push vers le distant",
    ]

    logger.log_info("Feuille de route :")
    for i, etape in enumerate(feuille_route, 1):
        logger.log_info(f"  Étape {i}: {etape}")

    # DRY RUN: afficher simulation et sortir
    if arguments.dry_run:
        afficher_simulation(ia_choisie, fichiers_a_analyser)
        return

    # 1) Génération du message de commit
    commit_classe = IaAssistantCommitFactory.get_commit_class(ia_choisie)
    assistant = commit_classe(fichiers_a_analyser)
    assistant.detecter_fichiers()

    diff_contenu = assistant.get_diff()
    if not diff_contenu.strip():
        logger.log_warn("Aucun changement détecté. Rien à faire.")
        return

    logger.log_info("Étape 1/5 — Génération du message de commit")
    try:
        message = assistant.generer_message_commit()
        logger.log_console(f"Message généré :\n{message}")
    except Exception as e:
        logger.log_error(f"Erreur lors de la génération du message : {e}")
        return

    # 2) Incrémentation de la version (si supportée)
    logger.log_info("Étape 2/5 — Incrémentation de la version")
    increment_done = False
    try:
        if hasattr(assistant, "incrementer_version"):
            nouvelle_version = assistant.incrementer_version()
            logger.log_success(f"Version incrémentée : {nouvelle_version}")
            increment_done = True
        else:
            # Tentative d'utiliser python_commun.versioning si disponible
            try:
                from python_commun.version.versioning import increment_project_version

                nouvelle_version = increment_project_version()
                logger.log_success(f"Version incrémentée via python_commun: {nouvelle_version}")
                increment_done = True
            except Exception:
                logger.log_info("Aucune routine d'incrémentation de version détectée — étape ignorée.")
    except Exception as e:
        logger.log_warn(f"Échec de l'incrémentation de version : {e}")

    # 3) Mise à jour du CHANGELOG (si supportée)
    logger.log_info("Étape 3/5 — Mise à jour du CHANGELOG")
    changelog_done = False
    try:
        if hasattr(assistant, "mettre_a_jour_changelog"):
            assistant.mettre_a_jour_changelog(message=message)
            logger.log_success("CHANGELOG mis à jour via l'assistant.")
            changelog_done = True
        else:
            # Fallback minimal : proposer au user d'ouvrir le CHANGELOG pour édition
            logger.log_info("Aucune routine automatique de mise à jour du CHANGELOG détectée.")
            ouvrir = _demander_confirmation("Ouvrir CHANGELOG.md pour édition manuelle ? (y/n)", valeur_defaut="n")
            if ouvrir in ("y", "o"):
                try:
                    editer_texte_avec_editeur("CHANGELOG.md")
                    changelog_done = True
                except Exception as e:
                    logger.log_warn(f"Impossible d'éditer CHANGELOG.md : {e}")
    except Exception as e:
        logger.log_warn(f"Erreur lors de la mise à jour du CHANGELOG : {e}")

    # 4) Commit : code + version + CHANGELOG
    logger.log_info("Étape 4/5 — Commit des fichiers")
    try:
        # Si l'assistant fournit une méthode de validation de commit, l'utiliser
        if hasattr(assistant, "valider_commit"):
            assistant.valider_commit(message)
            logger.log_success("Commit effectué via l'assistant.")
        else:
            # Stager tous les fichiers détectés et effectuer un commit générique
            ajouter_fichiers_a_index(assistant.repo, fichiers_a_analyser)
            if a_des_changements_indexes(assistant.repo):
                effectuer_commit_avec_message(assistant.repo, message)
                logger.log_success("Commit effectué.")
            else:
                logger.log_warn("Aucun changement indexé — pas de commit effectué.")
    except KeyboardInterrupt:
        logger.log_warn("Opération annulée par l'utilisateur pendant le commit.")
        return
    except Exception as e:
        logger.log_error(f"Erreur lors du commit : {e}")
        return

    # 5) Push vers distant
    logger.log_info("Étape 5/5 — Push vers le distant")
    try:
        if _demander_confirmation("Pousser vers le distant ? (y/n)", valeur_defaut="n") in ("y", "o"):
            try:
                pousser_vers_distant(assistant.repo)
                logger.log_success("Push effectué.")
            except Exception as e:
                logger.log_warn(f"Échec du push automatique : {e}")
                logger.log_info("Vous pouvez pousser manuellement avec 'git push'.")
        else:
            logger.log_info("Push ignoré par l'utilisateur.")
    except Exception as e:
        logger.log_warn(f"Erreur lors de l'étape de push : {e}")


if __name__ == "__main__":
    main()
