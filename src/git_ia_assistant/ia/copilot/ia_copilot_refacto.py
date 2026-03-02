#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from git_ia_assistant.core.definition.ia_assistant_refacto import IaAssistantRefacto
from python_commun.ai.copilot import envoyer_prompt_copilot
from python_commun.logging.logger import logger

class IaCopilotRefacto(IaAssistantRefacto):
    def refactoriser_code(self) -> str:
        prompt = self.generer_prompt()
        logger.log_info("Copilot réfléchit à la refactorisation...")
        return envoyer_prompt_copilot(prompt)
