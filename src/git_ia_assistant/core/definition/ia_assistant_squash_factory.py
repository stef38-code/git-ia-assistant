#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    ia_assistant_squash_factory - Factory pour instancier la classe de squash IA

DESCRIPTION
    Fournit la classe adaptée pour la suggestion de squash selon l'IA choisie.

FUNCTIONS
    get_squash_class(nom_ia: str) -> type
        Retourne la classe de squash IA selon le nom fourni.

DATA
    Aucune
"""

from git_ia_assistant.core.definition.ia_assistant_squash import IaAssistantSquash
from git_ia_assistant.ia.copilot.ia_copilot_squash import IaCopilotSquash
from git_ia_assistant.ia.gemini.ia_gemini_squash import IaGeminiSquash
from git_ia_assistant.ia.ollama.ia_ollama_squash import IaOllamaSquash


class IaAssistantSquashFactory:
    """
    Factory pour obtenir la classe de squash IA selon l'IA choisie.
    """

    @staticmethod
    def get_squash_class(nom_ia: str) -> type:
        """
        Retourne la classe de squash IA selon le nom fourni.
        :param nom_ia: Nom de l'IA ('copilot', 'gemini', 'ollama')
        :return: Classe correspondante
        :raises ValueError: Si le nom d'IA est inconnu
        """
        if nom_ia == "copilot":
            return IaCopilotSquash
        elif nom_ia == "gemini":
            return IaGeminiSquash
        elif nom_ia == "ollama":
            return IaOllamaSquash
        else:
            raise ValueError(f"IA inconnue : {nom_ia}")
