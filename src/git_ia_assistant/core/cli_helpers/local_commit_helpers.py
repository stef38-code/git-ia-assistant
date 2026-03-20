"""Fonctions spécifiques au mode local (non MCP) pour la génération de commits.

Utilise les wrappers git_ui_helpers et les helpers partagés (commit_cli_helpers).
"""
import os
from typing import List, Set
from python_commun.logging import logger
from git_ia_assistant.core.definition.ia_assistant_commit_factory import IaAssistantCommitFactory
from git_ia_assistant.core.cli_helpers.commit_cli_helpers import determiner_ia_choisie, detecter_fichiers
from git_ia_assistant.core.cli_helpers import git_ui_helpers as git_ui


def afficher_simulation_commit(ia_choisie: str, fichiers_a_analyser: List[str]) -> None:
    logger.log_info(f"[DRY-RUN] IA utilisée : {ia_choisie}")
    logger.log_info(f"[DRY-RUN] Fichiers analysés : {fichiers_a_analyser}")

    # pré-commit léger pour préparer l'index si nécessaire
    git_ui.git_pre_commit(fichiers_a_analyser)
    commit_classe = IaAssistantCommitFactory.get_commit_class(ia_choisie)
    assistant_commit = commit_classe(fichiers_a_analyser)
    assistant_commit.detecter_fichiers()

    logger.log_info(f"[DRY-RUN] Préparation des fichiers spécifiés : {', '.join(fichiers_a_analyser)}")
    prompt_simule = assistant_commit.get_diff()
    logger.log_console(f"[DRY-RUN] Prompt simulé (diff) :\n{prompt_simule}")


def generer_et_valider_commit(ia_choisie: str, fichiers_a_analyser: List[str]) -> None:
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

    try:
        assistant_commit.valider_commit(message_commit)
    except KeyboardInterrupt:
        logger.log_warn("Opération annulée par l'utilisateur.")


# fonctions d'optimisation (reprise et simplification depuis l'ancien commit_cli)

def _analyser_fichiers_partages(commits_suggeres: List[dict]) -> Set[str]:
    comptage_fichiers = {}
    for suggestion in commits_suggeres:
        for fichier_chemin in suggestion.get("files", []):
            comptage_fichiers[fichier_chemin] = comptage_fichiers.get(fichier_chemin, 0) + 1
    return {f for f, c in comptage_fichiers.items() if c > 1}


def _preparer_et_effectuer_un_commit(
    index: int,
    nombre_total: int,
    suggestion: dict,
    assistant_commit,
    fichiers_partages: Set[str]
) -> bool:
    fichiers_groupe = suggestion.get("files", [])
    if not fichiers_groupe:
        return True

    scope = f"({suggestion.get('scope')})" if suggestion.get('scope') else ""
    titre_commit = f"{suggestion.get('type')}{scope}: {suggestion.get('subject')}"
    corps_commit = suggestion.get("body", "")
    message_final = f"{titre_commit}\n\n{corps_commit}".strip()

    logger.log_console(f"\n--- Commit {index}/{nombre_total} ---")
    logger.log_console(f"Message : {titre_commit}")

    while True:
        choix_action = git_ui.demander_confirmation("Action : [y: valider, n: passer, e: éditer, q: quitter]")
        if choix_action == "y":
            break
        elif choix_action == "e":
            message_final = git_ui.editer_texte_avec_editeur(message_final)
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
            git_ui.ajouter_fichiers_interactif([fichier_chemin])
        else:
            git_ui.ajouter_fichiers_a_index(assistant_commit.repo, [fichier_chemin])

    # Validation du commit
    if git_ui.a_des_changements_indexes(assistant_commit.repo):
        git_ui.effectuer_commit_avec_message(assistant_commit.repo, message_final)
        logger.log_success(f"Commit {index} effectué : {titre_commit}")
    else:
        logger.log_warn(f"Aucun changement indexé pour le commit {index}. Passé.")

    return True


def gerer_optimisation_commit(ia_choisie: str, fichiers_a_analyser: List[str], mode_partiel: bool = False) -> None:
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

    git_ui.afficher_recapitulatif_suggestions(commits_suggeres, fichiers_partages)

    valider_tout = git_ui.demander_confirmation("\nProcéder à ces commits ? [y: oui, n: non, i: un par un]", valeur_defaut="y")
    if valider_tout in ("n", "no"):
        logger.log_warn("Opération annulée.")
        return

    # Désindexer tous les fichiers pour gérer les groupes proprement
    git_ui.reinitialiser_index(assistant_commit.repo)

    nombre_total_commits = len(commits_suggeres)
    for index, suggestion_commit in enumerate(commits_suggeres, 1):
        continuer_workflow = _preparer_et_effectuer_un_commit(
            index,
            nombre_total_commits,
            suggestion_commit,
            assistant_commit,
            fichiers_partages,
        )
        if not continuer_workflow:
            break

    logger.log_info("\nTraitement des commits terminé.")
    valider_push = git_ui.demander_confirmation("Pousser tous les commits sur le dépôt distant ? [y: oui, n: non]", valeur_defaut="n")
    if valider_push in ("y", "o"):
        git_ui.pousser_vers_distant(assistant_commit.repo)
        logger.log_success("git push effectué !")


# point d'entrée utilisé par le wrapper commit_cli
def main() -> None:
    from python_commun.cli.usage import usage
    import argparse
    import sys

    parser = argparse.ArgumentParser(add_help=False, description="Génère un message de commit avec l'IA choisie.")
    parser.add_argument("--ia", choices=["copilot", "gemini", "ollama"], default="copilot", help="IA à utiliser (défaut: copilot)")
    parser.add_argument("-f", "--fichier", nargs="*", help="Nom(s) de fichier à analyser")
    parser.add_argument("--dry-run", action="store_true", help="Simulation sans appel à l'IA")
    parser.add_argument("--optimise", action="store_true", help="Optimise en groupant en commits logiques")
    parser.add_argument("--partiel", action="store_true", help="Permet de séparer un fichier en plusieurs commits (nécessite --optimise)")
    parser.add_argument("-h", "--help", action="store_true", help="Afficher l'aide colorisée")

    args = parser.parse_args()
    if getattr(args, "help", False):
        usage(__file__)
        return

    ia_choisie = determiner_ia_choisie(parser, args)

    fichiers_a_analyser = args.fichier
    if not fichiers_a_analyser:
        from python_commun.git.git_core import liste_fichier_non_suivis_et_modifies
        fichiers_a_analyser = liste_fichier_non_suivis_et_modifies()
        if fichiers_a_analyser:
            logger.log_info(f"{len(fichiers_a_analyser)} fichier(s) modifié(s) ou non suivi(s) détecté(s).")

    if not fichiers_a_analyser:
        logger.log_warn("Aucun fichier à commiter. Le script est terminé.")
        return

    # Sécurité : Vérifier si des fichiers liés à un 'revert' sont présents
    if any("revert" in os.path.basename(f).lower() for f in fichiers_a_analyser):
        logger.log_warn("Attention : Des fichiers liés à un 'revert' ont été détectés. Soyez vigilant lors de l'optimisation.")

    if args.dry_run:
        afficher_simulation_commit(ia_choisie, fichiers_a_analyser)
    elif args.optimise:
        gerer_optimisation_commit(ia_choisie, fichiers_a_analyser, mode_partiel=args.partiel)
    else:
        if args.partiel:
            logger.log_error("L'option --partiel nécessite obligatoirement l'option --optimise.")
            return
        generer_et_valider_commit(ia_choisie, fichiers_a_analyser)
