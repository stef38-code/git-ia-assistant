#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Classe d'explication IA avec Gemini.
"""

from git_ia_assistant.core.definition.ia_assistant_explain import IaAssistantExplain
from python_commun.ai.gemini_utils import envoyer_prompt_gemini
from python_commun.logging.logger import logger

class IaGeminiExplain(IaAssistantExplain):
    """
    Explication de code via Gemini.
    """

    def expliquer_code(self) -> str:
        prompt = self.generer_prompt()
        logger.log_info("Gemini analyse le code...")
        return envoyer_prompt_gemini(prompt)
