#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from git_ia_assistant.core.definition.ia_assistant_refacto import IaAssistantRefacto
from python_commun.ai.gemini_utils import envoyer_prompt_gemini
from python_commun.logging.logger import logger

class IaGeminiRefacto(IaAssistantRefacto):
    def refactoriser_code(self) -> str:
        prompt = self.generer_prompt()
        logger.log_info("Gemini réfléchit à la refactorisation...")
        return envoyer_prompt_gemini(prompt)
