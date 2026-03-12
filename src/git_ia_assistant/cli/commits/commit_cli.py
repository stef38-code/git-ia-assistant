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
from typing import List, Dict, Set, Optional

# Ajout du chemin racine et de la librairie commune pour permettre l'import des modules du projet
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../libs/python_commun/src")))

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
    commit_classe = IaAssistantCommitFactory.get_commit_class(ia_choisie)
    assistant_commit = commit_classe(fichiers_a_analyser)

    assistant_commit.detecter_fichiers()

    # Vérification pour empêcher les commits vides
    diff_contenu = assistant_commit.get_diff()
    if not diff_contenu.strip():
        logger.log_warn("Aucun changement détecté dans les fichiers préparés. Le commit est annulé.")
        return

    logger.log_info(f"Génération du message de commit avec {ia_choisie}...")
    message_commit = assistant_commit.generer_message_commit()
    logger.log_console(f"Message généré par l'IA :\n{message_commit}")

    try:
        assistant_commit.valider_commit(message_commit)
    except KeyboardInterrupt:
        logger.log_warn("Opération annulée par l'utilisateur.")


def _demander_confirmation(message: str, valeur_defaut: str = "y") -> str:
    """
    Pose une question à l'utilisateur et retourne la réponse formatée.

    :param message: Message de la question.
    :param valeur_defaut: Valeur par défaut si l'utilisateur appuie sur Entrée.
    :return: Réponse de l'utilisateur en minuscules.
    """
    invite_saisie = f"{message} [défaut: {valeur_defaut}] : "
    reponse_utilisateur = input(invite_saisie).strip().lower()
    return reponse_utilisateur if reponse_utilisateur else valeur_defaut


def _analyser_fichiers_partages(commits_suggeres: List[dict]) -> Set[str]:
    """
    Identifie les fichiers présents dans plusieurs suggestions de commits.

    :param commits_suggeres: Liste des suggestions de l'IA.
    :return: Ensemble des chemins de fichiers partagés.
    """
    comptage_fichiers = {}
    for suggestion in commits_suggeres:
        for fichier_chemin in suggestion.get("files", []):
            comptage_fichiers[fichier_chemin] = comptage_fichiers.get(fichier_chemin, 0) + 1
    
    return {fichier_chemin for fichier_chemin, compteur in comptage_fichiers.items() if compteur > 1}


def _afficher_recapitulatif_suggestions(commits_suggeres: List[dict], fichiers_partages: Set[str]) -> None:
    """
    Affiche la liste des commits suggérés par l'IA.

    :param commits_suggeres: Liste des suggestions de l'IA.
    :param fichiers_partages: Ensemble des fichiers à découper.
    """
    logger.log_console(f"\n{len(commits_suggeres)} commit(s) suggéré(s) :\n")
    for index, suggestion in enumerate(commits_suggeres, 1):
        scope = f"({suggestion.get('scope')})" if suggestion.get("scope") else ""
        titre = f"{suggestion.get('type')}{scope}: {suggestion.get('subject')}"
        logger.log_console(f"[{index}] {titre}")
        for fichier_chemin in suggestion.get("files", []):
            suffixe_affichage = " (PARTIEL)" if fichier_chemin in fichiers_partages else ""
            logger.log_console(f"    - {fichier_chemin}{suffixe_affichage}")


def _preparer_et_effectuer_un_commit(
    index: int, 
    nombre_total: int, 
    suggestion: dict, 
    assistant_commit, 
    fichiers_partages: Set[str]
) -> bool:
    """
    Gère l'interaction et l'exécution d'un commit spécifique parmi les suggestions.

    :param index: Index du commit courant.
    :param nombre_total: Nombre total de commits suggérés.
    :param suggestion: Données du commit suggéré.
    :param assistant_commit: Instance de l'assistant commit.
    :param fichiers_partages: Ensemble des fichiers nécessitant un ajout interactif.
    :return: True si le workflow doit continuer, False si l'utilisateur a quitté prématurément.
    """
    fichiers_groupe = suggestion.get("files", [])
    if not fichiers_groupe:
        return True

    scope = f"({suggestion.get('scope')})" if suggestion.get("scope") else ""
    titre_commit = f"{suggestion.get('type')}{scope}: {suggestion.get('subject')}"
    corps_commit = suggestion.get("body", "")
    message_final = f"{titre_commit}\n\n{corps_commit}".strip()

    logger.log_console(f"\n--- Commit {index}/{nombre_total} ---")
    logger.log_console(f"Message : {titre_commit}")
    
    while True:
        choix_action = _demander_confirmation("Action : [y: valider, n: passer, e: éditer, q: quitter]")
        if choix_action == "y":
            break
        elif choix_action == "e":
            message_final = editer_texte_avec_editeur(message_final)
            titre_commit = message_final.split('\n')[0]
            logger.log_console(f"Nouveau message : {titre_commit}")
        elif choix_action == "n":
            return True
        elif choix_action == "q":
            logger.log_info("Fin prématurée de l'optimisation.")
            return False
        else:
            break

    # Préparation des fichiers (Stage)
    for fichier_chemin in fichiers_groupe:
        if fichier_chemin in fichiers_partages:
            logger.log_info(f"Découpage partiel pour : {fichier_chemin}")
            logger.log_console("INFO: Utilisez 'y' pour ajouter un bloc, 'n' pour l'ignorer.")
            ajouter_fichiers_interactif([fichier_chemin])
        else:
            ajouter_fichiers_a_index(assistant_commit.repo, [fichier_chemin])

    # Validation du commit
    if a_des_changements_indexes(assistant_commit.repo):
        effectuer_commit_avec_message(assistant_commit.repo, message_final)
        logger.log_success(f"Commit {index} effectué : {titre_commit}")
    else:
        logger.log_warn(f"Aucun changement indexé pour le commit {index}. Passé.")
    
    return True


def gerer_optimisation_commit(ia_choisie: str, fichiers_a_analyser: List[str], mode_partiel: bool = False) -> None:
    """
    Analyse les changements, propose un regroupement en commits logiques
    et gère le processus de commit pour chaque groupe.

    :param ia_choisie: Nom de l'IA sélectionnée.
    :param fichiers_a_analyser: Liste des fichiers ciblés.
    :param mode_partiel: Si True, permet le découpage des fichiers (git add -p).
    """
    commit_classe = IaAssistantCommitFactory.get_commit_class(ia_choisie)
    assistant_commit = commit_classe(fichiers_a_analyser)
    assistant_commit.detecter_fichiers()

    logger.log_info(f"Analyse des changements avec {ia_choisie} pour optimisation (mode partiel: {mode_partiel})...")
    commits_suggeres = assistant_commit.optimiser_commits(partiel=mode_partiel)

    if not commits_suggeres:
        logger.log_warn("Aucune optimisation possible ou erreur lors de l'analyse.")
        return

    fichiers_partages = _analyser_fichiers_partages(commits_suggeres)
    if fichiers_partages and not mode_partiel:
        logger.log_warn("L'IA a suggéré de découper certains fichiers mais le mode --partiel n'est pas activé.")
        logger.log_warn(f"Fichiers concernés : {', '.join(fichiers_partages)}")

    _afficher_recapitulatif_suggestions(commits_suggeres, fichiers_partages)

    valider_tout = _demander_confirmation("\nProcéder à ces commits ? [y: oui, n: non, i: un par un]")
    if valider_tout in ("n", "no"):
        logger.log_warn("Opération annulée.")
        return

    # Désindexer tous les fichiers pour gérer les groupes proprement
    reinitialiser_index(assistant_commit.repo)

    nombre_total_commits = len(commits_suggeres)
    for index, suggestion_commit in enumerate(commits_suggeres, 1):
        continuer_workflow = _preparer_et_effectuer_un_commit(
            index, 
            nombre_total_commits, 
            suggestion_commit, 
            assistant_commit, 
            fichiers_partages
        )
        if not continuer_workflow:
            break

    logger.log_info("\nTraitement des commits terminé.")
    valider_push = _demander_confirmation("Pousser tous les commits sur le dépôt distant ? [y: oui, n: non]", valeur_defaut="n")
    if valider_push in ("y", "o"):
        pousser_vers_distant(assistant_commit.repo)
        logger.log_success("git push effectué !")


def main() -> None:
    """
    Point d'entrée principal du script.
    """
    from python_commun.cli.usage import usage

    arguments_cli = _parser_options()
    if getattr(arguments_cli, "help", False):
        usage(__file__)
        return
    
    # Détermination de l'IA à utiliser en respectant la priorité demandée
    ia_valides = {"copilot", "gemini", "ollama"}
    ia_environnement = os.getenv("IA_SELECTED")
    ia_option_presente = "--ia" in sys.argv

    if not ia_option_presente and ia_environnement in ia_valides:
        ia_choisie = ia_environnement
    else:
        ia_choisie = arguments_cli.ia

    fichiers_a_analyser = arguments_cli.fichier
    if not fichiers_a_analyser:
        fichiers_a_analyser = liste_fichier_non_suivis_et_modifies()
        if fichiers_a_analyser:
            logger.log_info(
                f"{len(fichiers_a_analyser)} fichier(s) modifié(s) ou non suivi(s) détecté(s)."
            )

    if not fichiers_a_analyser:
        logger.log_warn("Aucun fichier à commiter. Le script est terminé.")
        return

    # Sécurité : Vérifier si des fichiers liés à un 'revert' sont présents
    if any("revert" in fichier_nom.lower() for fichier_chemin in fichiers_a_analyser for fichier_nom in [os.path.basename(fichier_chemin)]):
        logger.log_warn("Attention : Des fichiers liés à un 'revert' ont été détectés. Soyez vigilant lors de l'optimisation.")

    if arguments_cli.dry_run:
        afficher_simulation_commit(ia_choisie, fichiers_a_analyser)
    elif arguments_cli.optimise:
        gerer_optimisation_commit(ia_choisie, fichiers_a_analyser, mode_partiel=arguments_cli.partiel)
    else:
        if arguments_cli.partiel:
            logger.log_error("L'option --partiel nécessite obligatoirement l'option --optimise.")
            return
        generer_et_valider_commit(ia_choisie, fichiers_a_analyser)


if __name__ == "__main__":
    main()
