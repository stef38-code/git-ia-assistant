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
from git_ia_assistant.core.definition.ia_assistant import IaAssistant
from python_commun.logging.logger import logger


class IaAssistantTypeReview(IaAssistant):
    """
    Classe mère pour la revue de code par type de langage et IA.
    """

    def __init__(self, fichiers, version=None):
        super().__init__()
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

    def generer_prompt_review(self) -> str:
        """
        Génère le prompt pour la revue de code, incluant le contexte des imports.
        """
        if not self.fichiers:
            return ""

        chemin_fichier = self.fichiers[0]
        with open(chemin_fichier, "r", encoding="utf-8") as f:
            code = f.read()

        contexte_imports = self._extraire_contexte_imports(chemin_fichier, code)
        
        # Le prompt template doit être chargé par les sous-classes pour avoir le bon nom de fichier
        raise NotImplementedError

    def _extraire_contexte_imports(self, chemin_fichier: str, code: str) -> str:
        """
        Tente d'extraire le contenu des fichiers importés (interfaces, types) pour donner du contexte.
        """
        import re
        dossier_base = os.path.dirname(chemin_fichier)
        contexte = ""
        
        # Exemple simple pour Python
        if chemin_fichier.endswith(".py"):
            imports = re.findall(r"from (\..+) import (.+)", code)
            for module, _ in imports:
                # Tentative de lecture du fichier local (simplifié)
                target_path = os.path.join(dossier_base, module.replace(".", "/") + ".py")
                if os.path.exists(target_path):
                    try:
                        with open(target_path, "r", encoding="utf-8") as f:
                            contexte += f"\n--- Contexte Import ({module}) ---\n"
                            contexte += f.read()[:2000] # Limite par fichier
                    except:
                        pass
        return contexte

    def generer_review(self, repo_path=None):
        raise NotImplementedError
