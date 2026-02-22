#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    ia_assistant_explain - Classe mère pour l'explication de code IA.
"""

from git_ia_assistant.core.definition.ia_assistant import IaAssistant
from python_commun.ai.prompt import charger_prompt, formatter_prompt

class IaAssistantExplain(IaAssistant):
    """
    Classe de base pour expliquer le code avec l'IA.
    """

    def __init__(self, fichier: str):
        super().__init__()
        self.fichier = fichier

    def generer_prompt(self) -> str:
        """
        Génère le prompt pour l'explication du fichier.
        """
        with open(self.fichier, "r", encoding="utf-8") as f:
            code = f.read()
        
        template = charger_prompt("explain_prompt.md", self.dossier_prompts)
        return formatter_prompt(template, code=code)

    def expliquer_code(self) -> str:
        """
        Méthode abstraite à implémenter par les sous-classes.
        """
        raise NotImplementedError
