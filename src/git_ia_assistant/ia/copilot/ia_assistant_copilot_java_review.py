#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Revue Java avec Copilot.
Exemple :
    review = IaAssistantCopilotJavaReview('monfichier.java', version='17')
    review.generer_review()
"""

from git_ia_assistant.core.definition.ia_assistant_type_review import IaAssistantTypeReview
from python_commun.ai.prompt import charger_prompt, formatter_prompt
from python_commun.ai.copilot import envoyer_prompt_copilot
from python_commun.logging.logger import logger


class IaAssistantCopilotJavaReview(IaAssistantTypeReview):
    """
    Revue Java avec Copilot.
    """

    def generer_review(self):
        prompt_template = charger_prompt("java_review_prompt.md", self.dossier_prompts)
        with open(self.fichier, "r", encoding="utf-8") as f:
            code = f.read()
        prompt = formatter_prompt(
            prompt_template, code=code, version=self.version or "17"
        )
        logger.log_info("Copilot réfléchit à la revue Java...")
        reponse = envoyer_prompt_copilot(prompt)
        logger.log_console(reponse)
