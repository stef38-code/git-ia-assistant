#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    ia_assistant_squash - Classe mère pour la suggestion de squash IA.

DESCRIPTION
    Cette classe de base définit l'interface et la logique commune pour la
    génération de suggestions de squash de commits assistée par IA. Elle gère
    la récupération des derniers commits, le formatage de leur liste pour
    l'IA, et la génération du prompt générique pour le squash.

FUNCTIONS
    recuperer_commits()
        Méthode abstraite pour récupérer les derniers commits à traiter.
    formatter_liste_commits(liste_commits)
        Formate la liste des commits pour le prompt IA.
    generer_prompt_squash(liste_commits)
        Génère le prompt générique pour le squash IA.
    generer_squash(liste_commits)
        Méthode abstraite pour envoyer le prompt à l'IA et retourner la suggestion de squash.

DATA
    nb_commits: int
        Le nombre de commits à prendre en compte pour la suggestion.
    repo: git.Repo
        L'objet GitPython représentant le dépôt.
"""

from git_ia_assistant.core.definition.ia_assistant import IaAssistant


class IaAssistantSquash(IaAssistant):
    """
    Classe mère pour la suggestion de squash IA.
    """

    def __init__(self, nb_commits):
        super().__init__()
        self.nb_commits = nb_commits

    def recuperer_commits(self):
        raise NotImplementedError

    def formatter_liste_commits(self, liste_commits):
        """
        Formate la liste des commits pour le prompt IA.
        :param liste_commits: Liste des objets commit
        :return: Chaîne formatée
        """
        return "\n".join(
            f"- {commit_git.hexsha[:7]}: {commit_git.summary}"
            for commit_git in liste_commits
        )

    def generer_prompt_squash(self, liste_commits):
        """
        Génère le prompt générique pour le squash IA.
        :param liste_commits: Liste des objets commit
        :return: Prompt textuel
        """
        prompt_squash = "Squash les commits suivants :\n"
        prompt_squash += self.formatter_liste_commits(liste_commits)
        return prompt_squash

    def generer_squash(self, liste_commits):
        raise NotImplementedError
