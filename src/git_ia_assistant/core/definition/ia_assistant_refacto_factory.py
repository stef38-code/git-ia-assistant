#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    ia_assistant_refacto_factory - Factory pour instancier les classes de refactorisation IA.
"""

import importlib

class IaAssistantRefactoFactory:
    """
    Factory pour obtenir la classe de refactorisation IA.
    """

    IA_MODULES = {
        "copilot": "git_ia_assistant.ia.copilot.ia_copilot_refacto",
        "gemini": "git_ia_assistant.ia.gemini.ia_gemini_refacto",
        "ollama": "git_ia_assistant.ia.ollama.ia_ollama_refacto",
    }
    IA_CLASSES = {
        "copilot": "IaCopilotRefacto",
        "gemini": "IaGeminiRefacto",
        "ollama": "IaOllamaRefacto",
    }

    @classmethod
    def get_refacto_class(cls, ia: str):
        module_name = cls.IA_MODULES.get(ia)
        class_name = cls.IA_CLASSES.get(ia)
        if not module_name or not class_name:
            raise ValueError(f"IA non supportée pour la refactorisation : {ia}")
        
        module = importlib.import_module(module_name)
        return getattr(module, class_name)
