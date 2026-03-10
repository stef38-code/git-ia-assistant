#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    ia_assistant_test_factory - Factory pour instancier les classes de génération de tests IA.
"""

import importlib

class IaAssistantTestFactory:
    """
    Factory pour obtenir la classe de génération de tests IA.
    """

    IA_MODULES = {
        "copilot": "git_ia_assistant.ia.copilot.ia_copilot_test",
        "gemini": "git_ia_assistant.ia.gemini.ia_gemini_test",
        "ollama": "git_ia_assistant.ia.ollama.ia_ollama_test",
    }
    IA_CLASSES = {
        "copilot": "IaCopilotTest",
        "gemini": "IaGeminiTest",
        "ollama": "IaOllamaTest",
    }

    @classmethod
    def get_test_class(cls, ia: str):
        module_name = cls.IA_MODULES.get(ia)
        class_name = cls.IA_CLASSES.get(ia)
        if not module_name or not class_name:
            raise ValueError(f"IA non supportée pour les tests : {ia}")
        
        module = importlib.import_module(module_name)
        return getattr(module, class_name)
