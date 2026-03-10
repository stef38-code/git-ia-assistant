#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from git_ia_assistant.core.definition.ia_assistant_refacto import IaAssistantRefacto
from python_commun.ai.ollama_utils import appeler_ollama
from python_commun.logging.logger import logger

class IaOllamaRefacto(IaAssistantRefacto):
    def refactoriser_code(self) -> str:
        prompt = self.generer_prompt()
        logger.log_info("Ollama réfléchit à la refactorisation...")
        return appeler_ollama(prompt)
