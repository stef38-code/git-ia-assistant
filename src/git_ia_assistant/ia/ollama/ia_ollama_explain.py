#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Classe d'explication IA avec Ollama.
"""

from git_ia_assistant.core.definition.ia_assistant_explain import IaAssistantExplain
from python_commun.ai.ollama_utils import appeler_ollama
from python_commun.logging.logger import logger

class IaOllamaExplain(IaAssistantExplain):
    """
    Explication de code via Ollama.
    """

    def expliquer_code(self) -> str:
        prompt = self.generer_prompt()
        logger.log_info("Ollama analyse le code...")
        return appeler_ollama(prompt)
