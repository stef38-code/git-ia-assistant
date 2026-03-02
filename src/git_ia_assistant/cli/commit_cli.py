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
    --optimise                  Analyse et propose un regroupement en commits logiques
    --partiel                   Permet de découper un fichier en plusieurs commits (nécessite --optimise)
    -h, --help                  Afficher l'aide colorisée

VARIABLES D'ENVIRONNEMENT
    IA_SELECTED                 Choix de l'IA (copilot|gemini|ollama) utilisé uniquement si --ia est absent

EXEMPLES
    python ia_assistant_commit.py --dry-run
    python ia_assistant_commit.py --optimise
    python ia_assistant_commit.py --optimise --partiel
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
import tempfile
from typing import List

# Ajout du chemin racine et de la librairie commune pour permettre l'import des modules du projet
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../libs/python_commun/src")))

from python_commun.logging import logger
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
        "--optimise", action="store_true", help="Optimise en groupant en commits logiques"
    )
    parser.add_argument(
        "--partiel", action="store_true", help="Permet de séparer un fichier en plusieurs commits (nécessite --optimise)"
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


def _demander_confirmation(message: str, defaut: str = "y") -> str:
    """
    Pose une question à l'utilisateur et retourne la réponse formatée.
    """
    prompt = f"{message} [défaut: {defaut}] : "
    reponse = input(prompt).strip().lower()
    return reponse if reponse else defaut


def gerer_optimisation_commit(ia_choisie: str, fichiers_a_analyser: List[str], partiel: bool = False) -> None:
    """
    Analyse les changements, propose un regroupement en commits logiques
    et gère le processus de commit pour chaque groupe.

    :param ia_choisie: Nom de l'IA sélectionnée.
    :param fichiers_a_analyser: Liste des fichiers ciblés.
    :param partiel: Si True, permet le découpage des fichiers (git add -p).
    """
    commit_classe = IaAssistantCommitFactory.get_commit_class(ia_choisie)
    assistant_commit = commit_classe(fichiers_a_analyser)
    assistant_commit.detecter_fichiers()

    logger.log_info(f"Analyse des changements avec {ia_choisie} pour optimisation (mode partiel: {partiel})...")
    commits_suggeres = assistant_commit.optimiser_commits(partiel=partiel)

    if not commits_suggeres:
        logger.log_warn("Aucune optimisation possible ou erreur lors de l'analyse.")
        return

    # Analyse des fichiers partagés (présents dans plusieurs commits)
    comptage_fichiers = {}
    for suggestion in commits_suggeres:
        for f in suggestion.get("files", []):
            comptage_fichiers[f] = comptage_fichiers.get(f, 0) + 1
    
    fichiers_partages = {f for f, count in comptage_fichiers.items() if count > 1}
    if fichiers_partages and not partiel:
        logger.log_warn("L'IA a suggéré de découper certains fichiers mais le mode --partiel n'est pas activé.")
        logger.log_warn(f"Fichiers concernés : {', '.join(fichiers_partages)}")
        # On pourrait ici choisir d'ignorer les doublons ou de forcer le mode partiel.
        # Par sécurité, on continue mais on avertit que le premier commit prendra tout le fichier.

    logger.log_console(f"\n{len(commits_suggeres)} commit(s) suggéré(s) :\n")
    for i, suggestion in enumerate(commits_suggeres, 1):
        scope = f"({suggestion.get('scope')})" if suggestion.get("scope") else ""
        titre = f"{suggestion.get('type')}{scope}: {suggestion.get('subject')}"
        logger.log_console(f"[{i}] {titre}")
        for f in suggestion.get("files", []):
            suffixe = " (PARTIEL)" if f in fichiers_partages else ""
            logger.log_console(f"    - {f}{suffixe}")

    valider_tout = _demander_confirmation("\nProcéder à ces commits ? [y: oui, n: non, i: un par un]")
    if valider_tout in ("n", "no"):
        logger.log_warn("Opération annulée.")
        return

    # Un-stage all files first to handle specific groups
    reinitialiser_index(assistant_commit.repo)

    for i, suggestion in enumerate(commits_suggeres, 1):
        files = suggestion.get("files", [])
        if not files:
            continue

        scope = f"({suggestion.get('scope')})" if suggestion.get("scope") else ""
        titre = f"{suggestion.get('type')}{scope}: {suggestion.get('subject')}"
        body = suggestion.get("body", "")
        message = f"{titre}\n\n{body}".strip()

        logger.log_console(f"\n--- Commit {i}/{len(commits_suggeres)} ---")
        logger.log_console(f"Message : {titre}")
        
        while True:
            choix = _demander_confirmation("Action : [y: valider, n: passer, e: éditer, q: quitter]")
            if choix == "y":
                break
            elif choix == "e":
                message = editer_texte_avec_editeur(message)
                titre = message.split('\n')[0]
                logger.log_console(f"Nouveau message : {titre}")
                continue
            elif choix == "n":
                files = [] # On vide la liste pour ne pas faire le commit
                break
            elif choix == "q":
                logger.log_info("Fin prématurée de l'optimisation.")
                return
            else:
                break

        if not files:
            continue

        # Stage files
        for f in files:
            if f in fichiers_partages:
                logger.log_info(f"Découpage partiel pour : {f}")
                logger.log_console("INFO: Utilisez 'y' pour ajouter un bloc, 'n' pour l'ignorer.")
                ajouter_fichiers_interactif([f])
            else:
                ajouter_fichiers_a_index(assistant_commit.repo, [f])

        # Effectuer le commit
        if a_des_changements_indexes(assistant_commit.repo):
            effectuer_commit_avec_message(assistant_commit.repo, message)
            logger.log_success(f"Commit {i} effectué : {titre}")
        else:
            logger.log_warn(f"Aucun changement indexé pour le commit {i}. Passé.")

    logger.log_info("\nTraitement des commits terminé.")
    push = _demander_confirmation("Pousser tous les commits sur le dépôt distant ? [y: oui, n: non]", defaut="n")
    if push in ("y", "o"):
        pousser_vers_distant(assistant_commit.repo)
        logger.log_success("git push effectué !")


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

    # Sécurité : Vérifier si des commits de type 'revert' sont présents pour avertir l'utilisateur
    if fichiers_a_analyser and any("revert" in f.lower() for f in fichiers_a_analyser):
        logger.log_warn("Attention : Des fichiers liés à un 'revert' ont été détectés. Soyez vigilant lors de l'optimisation.")

    if args.dry_run:
        afficher_simulation_commit(ia_choisie, fichiers_a_analyser)
    elif args.optimise:
        gerer_optimisation_commit(ia_choisie, fichiers_a_analyser, partiel=args.partiel)
    else:
        if args.partiel:
            logger.log_error("L'option --partiel nécessite obligatoirement l'option --optimise.")
            return
        generer_et_valider_commit(ia_choisie, fichiers_a_analyser)


if __name__ == "__main__":
    main()
