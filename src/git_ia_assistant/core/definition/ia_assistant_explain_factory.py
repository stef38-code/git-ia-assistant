#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    ia_assistant_explain_factory - Factory pour instancier les classes d'explication de code IA.
"""

import importlib

class IaAssistantExplainFactory:
    """
    Factory pour obtenir la classe d'explication IA selon l'IA choisie.
    """

    IA_MODULES = {
        "copilot": "git_ia_assistant.ia.copilot.ia_copilot_explain",
        "gemini": "git_ia_assistant.ia.gemini.ia_gemini_explain",
        "ollama": "git_ia_assistant.ia.ollama.ia_ollama_explain",
    }
    IA_CLASSES = {
        "copilot": "IaCopilotExplain",
        "gemini": "IaGeminiExplain",
        "ollama": "IaOllamaExplain",
    }

    @classmethod
    def get_explain_class(cls, ia: str):
        module_name = cls.IA_MODULES.get(ia)
        class_name = cls.IA_CLASSES.get(ia)
        if not module_name or not class_name:
            raise ValueError(f"IA inconnue ou non supportée pour l'explication : {ia}")
        
        module = importlib.import_module(module_name)
        return getattr(module, class_name)
