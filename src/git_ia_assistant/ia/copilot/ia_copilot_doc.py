#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from git_ia_assistant.core.definition.ia_assistant_doc import IaAssistantDoc
from python_commun.ai.copilot import envoyer_prompt_copilot
from python_commun.logging.logger import logger

class IaCopilotDoc(IaAssistantDoc):
    def generer_doc(self) -> str:
        prompt = self.generer_prompt()
        logger.log_info(f"Copilot génère la documentation ({self.doc_format})...")
        return envoyer_prompt_copilot(prompt)
