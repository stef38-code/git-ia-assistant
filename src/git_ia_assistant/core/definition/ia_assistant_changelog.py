#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    ia_assistant_changelog - Classe mère pour la génération de changelog IA.

DESCRIPTION
    Cette classe de base définit l'interface et la logique commune pour la
    génération de changelogs assistée par IA. Elle gère l'initialisation du
    dépôt Git et expose les méthodes abstraites pour récupérer les commits
    et générer le changelog final.

FUNCTIONS
    recuperer_commits()
        Méthode abstraite pour récupérer les commits du dépôt.
    generer_changelog(messages)
        Méthode abstraite pour générer le changelog à partir des messages de commit.

DATA
    limite: int
        Le nombre de commits à traiter.
    repo: git.Repo
        L'objet GitPython représentant le dépôt.
"""

from git_ia_assistant.core.definition.ia_assistant import IaAssistant


class IaAssistantChangelog(IaAssistant):
    """
    Classe mère pour la génération de changelog IA.
    """

    def __init__(self, limite):
        super().__init__()
        self.limite = limite

    def recuperer_commits(self):
        raise NotImplementedError

    def generer_changelog(self, messages):
        raise NotImplementedError
