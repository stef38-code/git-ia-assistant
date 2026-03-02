#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from git_ia_assistant.core.definition.ia_assistant_doc import IaAssistantDoc
from python_commun.ai.gemini_utils import envoyer_prompt_gemini
from python_commun.logging.logger import logger

class IaGeminiDoc(IaAssistantDoc):
    def generer_doc(self) -> str:
        prompt = self.generer_prompt()
        logger.log_info(f"Gemini génère la documentation ({self.doc_format})...")
        return envoyer_prompt_gemini(prompt)
