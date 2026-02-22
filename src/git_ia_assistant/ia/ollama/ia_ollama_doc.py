#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from git_ia_assistant.core.definition.ia_assistant_doc import IaAssistantDoc
from python_commun.ai.ollama_utils import appeler_ollama
from python_commun.logging.logger import logger

class IaOllamaDoc(IaAssistantDoc):
    def generer_doc(self) -> str:
        prompt = self.generer_prompt()
        logger.log_info(f"Ollama génère la documentation ({self.doc_format})...")
        return appeler_ollama(prompt)
