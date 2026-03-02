#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from git_ia_assistant.core.definition.ia_assistant_test import IaAssistantTest
from python_commun.ai.ollama_utils import appeler_ollama
from python_commun.logging.logger import logger

class IaOllamaTest(IaAssistantTest):
    def generer_tests(self, framework_version: str = "latest") -> str:
        prompt = self.generer_prompt(framework_version)
        logger.log_info(f"Ollama génère les tests ({self.test_framework})...")
        return appeler_ollama(prompt)
