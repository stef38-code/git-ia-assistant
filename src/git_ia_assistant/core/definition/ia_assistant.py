#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    ia_assistant - Classe mère de base pour tous les assistants IA.

DESCRIPTION
    Cette classe de base abstraite fournit une structure commune pour tous
    les assistants basés sur l'IA dans ce projet. Elle initialise les ressources
    partagées, comme la connexion à un dépôt Git, assurant ainsi que toutes
    les sous-classes ont accès aux fonctionnalités de base de Git.

FUNCTIONS
    Aucune fonction publique spécifique, les fonctions sont définies dans les sous-classes.

DATA
    repo: git.Repo
        L'objet GitPython représentant le dépôt Git du projet.
"""

import os
import git
from python_commun.logging import logger


class IaAssistant:
    """
    Classe de base qui initialise le dépôt Git commun à tous les assistants.
    """

    def __init__(self, require_repo: bool = True):
        self.dossier_prompts = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "prompts")
        )
        self.repo = None
        if require_repo:
            try:
                self.repo = git.Repo(search_parent_directories=True)
            except (git.InvalidGitRepositoryError, git.NoSuchPathError):
                logger.die("Le répertoire actuel n'est pas un dépôt Git.")
                raise
