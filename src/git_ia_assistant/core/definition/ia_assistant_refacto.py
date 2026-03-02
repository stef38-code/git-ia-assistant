#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    ia_assistant_refacto - Classe mère pour la refactorisation de code IA.
"""

import os
from git_ia_assistant.core.definition.ia_assistant import IaAssistant
from python_commun.ai.prompt import charger_prompt, formatter_prompt
from python_commun.system.system import detect_lang_repo

class IaAssistantRefacto(IaAssistant):
    """
    Classe de base pour refactoriser le code avec l'IA.
    """

    def __init__(self, fichier: str, version: str = None):
        super().__init__()
        self.fichier = fichier
        self.version = version

    def generer_prompt(self) -> str:
        """
        Génère le prompt pour la refactorisation.
        """
        with open(self.fichier, "r", encoding="utf-8") as f:
            code = f.read()
        
        langage = detect_lang_repo(os.path.dirname(self.fichier))
        version = self.version or "dernière version stable"

        template = charger_prompt("refacto_prompt.md", self.dossier_prompts)
        return formatter_prompt(template, code=code, langage=langage, version=version)

    def refactoriser_code(self) -> str:
        """
        Méthode abstraite.
        """
        raise NotImplementedError
