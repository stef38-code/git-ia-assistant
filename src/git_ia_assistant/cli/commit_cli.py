#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    ia_assistant_commit - Génère un message de commit avec l'IA choisie (Copilot, Gemini, Ollama).

DESCRIPTION
    Script Python pour générer un message de commit Git à l'aide d'une IA (Copilot, Gemini, Ollama).
    Permet d'analyser les fichiers modifiés/non suivis, de simuler le prompt, d'éditer le message et de pousser le commit.
    
    Sélection de l'IA:
      - Option --ia: choix explicite de l'IA (prioritaire si fournie)
      - Variable d'environnement IA_SELECTED: utilisée si l'option --ia est absente
      - Valeur par défaut: copilot

OPTIONS
    --ia copilot|gemini|ollama   Choix de l'IA (défaut: copilot; prioritaire sur IA_SELECTED si fournie)
    -f, --fichier <fichier(s)>  Liste des fichiers à analyser
    --dry-run                   Simulation, affiche le contexte sans appel à l'IA
    -h, --help                  Afficher l'aide colorisée

VARIABLES D'ENVIRONNEMENT
    IA_SELECTED                 Choix de l'IA (copilot|gemini|ollama) utilisé uniquement si --ia est absent

EXEMPLES
    python ia_assistant_commit.py --dry-run
    python ia_assistant_commit.py --ia gemini -f fichier1.py fichier2.py
    python ia_assistant_commit.py --ia ollama
    IA_SELECTED=gemini python ia_assistant_commit.py --dry-run
    IA_SELECTED=ollama python ia_assistant_commit.py -f fichier1.py

FUNCTIONS
    main() : Point d'entrée du script, gère les options et le workflow principal.
"""

import argparse
import os
import sys
from typing import List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from python_commun.logging import logger
from python_commun.git.git_core import liste_fichier_non_suivis_et_modifies
from git_ia_assistant.core.definition.ia_assistant_commit_factory import (
    IaAssistantCommitFactory,
)


def _parser_options() -> argparse.Namespace:
    """
    Analyse et retourne les arguments de la ligne de commande.

    :return: Un objet Namespace contenant les arguments parsés.
    """
    parser = argparse.ArgumentParser(
        add_help=False, description="Génère un message de commit avec l'IA choisie."
    )
    parser.add_argument(
        "--ia",
        choices=["copilot", "gemini", "ollama"],
        default="copilot",
        help="IA à utiliser (défaut: copilot)",
    )
    parser.add_argument(
        "-f", "--fichier", nargs="*", help="Nom(s) de fichier à analyser"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Simulation sans appel à l'IA"
    )
    parser.add_argument(
        "-h", "--help", action="store_true", help="Afficher l'aide colorisée"
    )
    return parser.parse_args()


def afficher_simulation_commit(ia_choisie: str, fichiers_a_analyser: List[str]) -> None:
    """
    Affiche le contexte de simulation (dry-run) sans faire d'appel à l'IA.

    :param ia_choisie: Nom de l'IA sélectionnée.
    :param fichiers_a_analyser: Liste des fichiers ciblés.
    """
    logger.log_info(f"[DRY-RUN] IA utilisée : {ia_choisie}")
    logger.log_info(f"[DRY-RUN] Fichiers analysés : {fichiers_a_analyser}")

    from python_commun.git.git_core import git_pre_commit

    git_pre_commit(fichiers_a_analyser)
    commit_classe = IaAssistantCommitFactory.get_commit_class(ia_choisie)
    assistant_commit = commit_classe(fichiers_a_analyser)
    assistant_commit.detecter_fichiers()

    logger.log_info(
        f"[DRY-RUN] Préparation des fichiers spécifiés : {', '.join(fichiers_a_analyser)}"
    )
    prompt_simule = assistant_commit.get_diff()
    logger.log_console(f"[DRY-RUN] Prompt simulé (diff) :\n{prompt_simule}")


def generer_et_valider_commit(ia_choisie: str, fichiers_a_analyser: List[str]) -> None:
    """
    Génère le message de commit avec l'IA et gère le processus de validation
    et de push avec l'utilisateur.

    :param ia_choisie: Nom de l'IA sélectionnée.
    :param fichiers_a_analyser: Liste des fichiers ciblés.
    """

    # git_pre_commit(fichiers_a_analyser)
    commit_classe = IaAssistantCommitFactory.get_commit_class(ia_choisie)
    assistant_commit = commit_classe(fichiers_a_analyser)

    assistant_commit.detecter_fichiers()

    # Vérification pour empêcher les commits vides
    diff = assistant_commit.get_diff()
    if not diff.strip():
        logger.log_warn("Aucun changement détecté dans les fichiers préparés. Le commit est annulé.")
        return

    logger.log_info(f"Génération du message de commit avec {ia_choisie}...")
    message_commit = assistant_commit.generer_message_commit()
    logger.log_console(f"Message généré par l'IA :\n{message_commit}")

    try:
        assistant_commit.valider_commit(message_commit)
    except KeyboardInterrupt:
        logger.log_warn("Opération annulée par l'utilisateur.")


def main() -> None:
    """
    Point d'entrée principal du script.
    """
    from python_commun.cli.usage import usage

    args = _parser_options()
    if getattr(args, "help", False):
        usage(__file__)
        return
    # Détermination de l'IA à utiliser en respectant la priorité demandée
    # 1) Si l'option --ia est fournie -> priorité à cette valeur
    # 2) Sinon, si la variable d'environnement IA_SELECTED est définie et valide -> on l'utilise
    # 3) Sinon -> on garde la valeur par défaut de l'argument (copilot)
    ia_valides = {"copilot", "gemini", "ollama"}
    ia_env = os.getenv("IA_SELECTED")
    ia_option_presente = "--ia" in sys.argv

    if not ia_option_presente and ia_env in ia_valides:
        ia_choisie = ia_env
    else:
        ia_choisie = args.ia

    fichiers_a_analyser = args.fichier
    if not fichiers_a_analyser:
        fichiers_a_analyser = liste_fichier_non_suivis_et_modifies()
        logger.log_info(
            f"Aucun fichier spécifié. {len(fichiers_a_analyser)} fichier(s) modifié(s) ou non suivi(s) détecté(s)."
        )

    if not fichiers_a_analyser:
        logger.log_warn("Aucun fichier à commiter. Le script est terminé.")
        return

    if args.dry_run:
        afficher_simulation_commit(ia_choisie, fichiers_a_analyser)
    else:
        generer_et_valider_commit(ia_choisie, fichiers_a_analyser)


if __name__ == "__main__":
    main()
