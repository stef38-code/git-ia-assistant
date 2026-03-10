#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from git_ia_assistant.core.definition.ia_assistant_test import IaAssistantTest
from python_commun.ai.copilot import envoyer_prompt_copilot
from python_commun.logging.logger import logger

class IaCopilotTest(IaAssistantTest):
    def generer_tests(self, framework_version: str = "latest") -> str:
        prompt = self.generer_prompt(framework_version)
        logger.log_info(f"Copilot génère les tests ({self.test_framework})...")
        return envoyer_prompt_copilot(prompt)
