#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    ia_assistant_doc_factory - Factory pour instancier les classes de génération de documentation IA.
"""

import importlib

class IaAssistantDocFactory:
    """
    Factory pour obtenir la classe de génération de documentation IA.
    """

    IA_MODULES = {
        "copilot": "git_ia_assistant.ia.copilot.ia_copilot_doc",
        "gemini": "git_ia_assistant.ia.gemini.ia_gemini_doc",
        "ollama": "git_ia_assistant.ia.ollama.ia_ollama_doc",
    }
    IA_CLASSES = {
        "copilot": "IaCopilotDoc",
        "gemini": "IaGeminiDoc",
        "ollama": "IaOllamaDoc",
    }

    @classmethod
    def get_doc_class(cls, ia: str):
        module_name = cls.IA_MODULES.get(ia)
        class_name = cls.IA_CLASSES.get(ia)
        if not module_name or not class_name:
            raise ValueError(f"IA non supportée pour la documentation : {ia}")
        
        module = importlib.import_module(module_name)
        return getattr(module, class_name)
