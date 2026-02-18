#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Factory pour instancier la classe de changelog IA selon l'IA choisie.
"""

from git_ia_assistant.copilot.ia_copilot_changelog import IaCopilotChangelog
from git_ia_assistant.gemini.ia_gemini_changelog import IaGeminiChangelog
from git_ia_assistant.ollama.ia_ollama_changelog import IaOllamaChangelog


class IaAssistantChangelogFactory:
    """
    Factory pour obtenir la classe de changelog IA selon l'IA choisie.
    """

    @staticmethod
    def get_changelog_class(nom_ia):
        if nom_ia == "copilot":
            return IaCopilotChangelog
        elif nom_ia == "gemini":
            return IaGeminiChangelog
        elif nom_ia == "ollama":
            return IaOllamaChangelog
        else:
            raise ValueError(f"IA inconnue : {nom_ia}")
