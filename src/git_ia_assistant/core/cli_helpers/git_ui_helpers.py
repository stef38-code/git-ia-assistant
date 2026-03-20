"""Wrappers pour opérations git et UI interactives réutilisables par les CLI.

But: ces wrappers délèguent à python_commun.git.git_core pour centraliser les points d'entrée
et faciliter les tests / mocking.
"""
from typing import List, Optional
import os
from python_commun.logging import logger
from python_commun.git import git_core as _git_core


# Git helpers ---------------------------------------------------------------

def git_pre_commit(fichiers: List[str]) -> None:
    """Appel wrapper de git_pre_commit (préparation légère avant dry-run)."""
    try:
        _git_core.git_pre_commit(fichiers)
    except Exception as e:
        logger.log_warn(f"git_pre_commit a échoué: {e}")


def editer_texte_avec_editeur(texte: str) -> str:
    """Ouvre l'éditeur défini par l'utilisateur pour éditer un texte et retourne le résultat."""
    return _git_core.editer_texte_avec_editeur(texte)


def ajouter_fichiers_interactif(fichiers: List[str]) -> None:
    return _git_core.ajouter_fichiers_interactif(fichiers)


def reinitialiser_index(repo) -> None:
    return _git_core.reinitialiser_index(repo)


def ajouter_fichiers_a_index(repo, fichiers: List[str]) -> None:
    return _git_core.ajouter_fichiers_a_index(repo, fichiers)


def a_des_changements_indexes(repo) -> bool:
    return _git_core.a_des_changements_indexes(repo)


def effectuer_commit_avec_message(repo, message: str) -> None:
    return _git_core.effectuer_commit_avec_message(repo, message)


def pousser_vers_distant(repo) -> None:
    try:
        return _git_core.pousser_vers_distant(repo)
    except Exception as e:
        logger.log_warn(f"Échec du push: {e}")


# UI helpers ----------------------------------------------------------------

def demander_confirmation(message: str, valeur_defaut: str = "y") -> str:
    """Demande une confirmation à l'utilisateur (retourne la réponse)."""
    invite_saisie = f"{message} [défaut: {valeur_defaut}] : "
    try:
        reponse_utilisateur = input(invite_saisie).strip().lower()
    except KeyboardInterrupt:
        logger.log_warn("Interruption utilisateur lors de la saisie.")
        return "q"
    return reponse_utilisateur if reponse_utilisateur else valeur_defaut


def afficher_recapitulatif_suggestions(commits_suggeres: List[dict], fichiers_partages: set) -> None:
    logger.log_console(f"\n{len(commits_suggeres)} commit(s) suggéré(s) :\n")
    for index, suggestion in enumerate(commits_suggeres, 1):
        scope = f"({suggestion.get('scope')})" if suggestion.get('scope') else ""
        titre = f"{suggestion.get('type')}{scope}: {suggestion.get('subject')}"
        logger.log_console(f"[{index}] {titre}")
        for fichier_chemin in suggestion.get('files', []):
            suffixe_affichage = " (PARTIEL)" if fichier_chemin in fichiers_partages else ""
            logger.log_console(f"    - {fichier_chemin}{suffixe_affichage}")
