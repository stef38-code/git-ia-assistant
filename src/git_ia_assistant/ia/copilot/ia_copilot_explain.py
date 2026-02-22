#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Classe d'explication IA avec Copilot.
"""

from git_ia_assistant.core.definition.ia_assistant_explain import IaAssistantExplain
from python_commun.ai.copilot import envoyer_prompt_copilot
from python_commun.logging.logger import logger

class IaCopilotExplain(IaAssistantExplain):
    """
    Explication de code via Copilot.
    """

    def expliquer_code(self) -> str:
        prompt = self.generer_prompt()
        logger.log_info("Copilot analyse le code...")
        return envoyer_prompt_copilot(prompt)
