#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    ia_assistant_commit_factory - Factory pour instancier la classe de commit IA.

DESCRIPTION
    Cette factory est responsable de créer et retourner la bonne instance de
    `IaAssistantCommit` (par exemple, `IaAssistantCopilotCommit` ou
    `IaAssistantGeminiCommit`) en fonction de l'IA choisie. Elle centralise
    la logique de sélection et d'importation dynamique des implémentations
    spécifiques à chaque IA pour la gestion des commits.

FUNCTIONS
    get_commit_class(ia: str) -> Type[IaAssistantCommit]
        Retourne la classe de commit IA appropriée selon l'IA choisie.

DATA
    IA_MODULES: Dict[str, str]
        Dictionnaire mappant les noms des IA aux chemins de leurs modules.
    IA_CLASSES: Dict[str, str]
        Dictionnaire mappant les noms des IA aux noms de leurs classes.
"""

from git_ia_assistant.core.definition.ia_assistant_commit import IaAssistantCommit
import importlib


class IaAssistantCommitFactory:
    """
    Factory pour instancier la bonne classe de commit IA.
    """

    IA_MODULES = {
        "copilot": "git_ia_assistant.ia.copilot.ia_assistant_copilot_commit",
        "gemini": "git_ia_assistant.ia.gemini.ia_assistant_gemini_commit",
        "ollama": "git_ia_assistant.ia.ollama.ia_assistant_ollama_commit",
    }
    IA_CLASSES = {
        "copilot": "IaAssistantCopilotCommit",
        "gemini": "IaAssistantGeminiCommit",
        "ollama": "IaAssistantOllamaCommit",
    }

    @classmethod
    def get_commit_class(cls, ia: str):
        module_name = cls.IA_MODULES.get(ia)
        class_name = cls.IA_CLASSES.get(ia)
        if not module_name or not class_name:
            return IaAssistantCommit
        module = importlib.import_module(module_name)
        return getattr(module, class_name)
