#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Revue Python avec Copilot.
Exemple :
    review = IaAssistantCopilotPythonReview('monfichier.py', version='3.10')
    review.generer_review()
"""

from git_ia_assistant.core.definition.ia_assistant_type_review import IaAssistantTypeReview
from python_commun.ai.prompt import charger_prompt, formatter_prompt
from python_commun.ai.copilot import envoyer_prompt_copilot
from python_commun.logging.logger import logger


class IaAssistantCopilotPythonReview(IaAssistantTypeReview):
    """
    Revue Python avec Copilot.
    """

    def generer_review(self):
        prompt_template = charger_prompt("python_review_prompt.md", self.dossier_prompts)
        with open(self.fichiers[0], "r", encoding="utf-8") as f:
            code = f.read()
        prompt = formatter_prompt(
            prompt_template, code=code, version=self.version or "3.x"
        )
        logger.log_info("Copilot réfléchit à la revue Python...")
        reponse = envoyer_prompt_copilot(prompt)
        logger.log_console(reponse)

    def generer_prompt_review(self):
        prompt_template = charger_prompt("python_review_prompt.md", self.dossier_prompts)
        with open(self.fichiers[0], "r", encoding="utf-8") as f:
            code = f.read()
        prompt = formatter_prompt(
            prompt_template, code=code, version=self.version or "3.x"
        )
        return prompt
