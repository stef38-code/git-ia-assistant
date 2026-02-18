#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    ia_assistant_type_review - Classe mère pour la revue de code par type de langage et IA.

DESCRIPTION
    Cette classe de base définit l'interface et la logique commune pour la
    revue de code assistée par IA, en prenant en compte le type de langage
    de programmation. Elle gère la validation des fichiers à réviser et
    expose une méthode abstraite pour générer la revue.

FUNCTIONS
    generer_review(repo_path=None)
        Méthode abstraite pour générer la revue de code.

DATA
    fichiers: list
        Liste des chemins des fichiers à réviser.
    version: Optional[str]
        Version du langage de programmation.
"""

import os
from python_commun.logging.logger import logger


class IaAssistantTypeReview:
    """
    Classe mère pour la revue de code par type de langage et IA.
    """

    def __init__(self, fichiers, version=None):
        self.fichiers = fichiers
        self.version = version
        # Vérifie l'existence de chaque fichier
        # Filtre les fichiers supprimés ou inexistants
        fichiers_existants = [f for f in self.fichiers if os.path.exists(f)]
        if not fichiers_existants:
            logger.log_warn(
                "Aucun fichier existant à reviewer. Aucun traitement effectué."
            )
        self.fichiers = fichiers_existants

    def generer_review(self, repo_path=None):
        raise NotImplementedError
