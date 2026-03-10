#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    ia_assistant_mr_factory - Factory pour instancier la classe de revue MR/PR IA.

DESCRIPTION
    Cette factory est responsable de créer et retourner la bonne instance de
    `IaAssistantMr` (par exemple, `IaCopilotMr`, `IaGeminiMr` ou
    `IaOllamaMr`) en fonction de l'IA choisie. Elle centralise
    la logique de sélection et d'importation dynamique des implémentations
    spécifiques à chaque IA pour la revue de Merge Request / Pull Request.

FUNCTIONS
    get_mr_class(ia: str) -> Type[IaAssistantMr]
        Retourne la classe de revue MR/PR IA appropriée selon l'IA choisie.

DATA
    IA_MODULES: Dict[str, str]
        Dictionnaire mappant les noms des IA aux chemins de leurs modules.
    IA_CLASSES: Dict[str, str]
        Dictionnaire mappant les noms des IA aux noms de leurs classes.
"""

from git_ia_assistant.core.definition.ia_assistant_mr import IaAssistantMr
import importlib


class IaAssistantMrFactory:
    """
    Factory pour instancier la bonne classe de revue MR/PR IA.
    """

    IA_MODULES = {
        "copilot": "git_ia_assistant.ia.copilot.ia_copilot_mr",
        "gemini": "git_ia_assistant.ia.gemini.ia_gemini_mr",
        "ollama": "git_ia_assistant.ia.ollama.ia_ollama_mr",
    }
    IA_CLASSES = {
        "copilot": "IaCopilotMr",
        "gemini": "IaGeminiMr",
        "ollama": "IaOllamaMr",
    }

    @classmethod
    def get_mr_class(cls, ia: str):
        """
        Retourne la classe de revue MR/PR appropriée selon l'IA choisie.

        :param ia: Le nom de l'IA (copilot, gemini, ollama).
        :return: La classe correspondante ou la classe de base si non trouvée.
        """
        module_name = cls.IA_MODULES.get(ia)
        class_name = cls.IA_CLASSES.get(ia)
        if not module_name or not class_name:
            return IaAssistantMr
        module = importlib.import_module(module_name)
        return getattr(module, class_name)
