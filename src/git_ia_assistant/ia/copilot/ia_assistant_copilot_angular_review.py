#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Revue Angular avec Copilot.
Exemple :
    review = IaAssistantCopilotAngularReview('monfichier.ts', version='16')
    review.generer_review()
"""

from git_ia_assistant.definition.ia_assistant_type_review import IaAssistantTypeReview
from python_commun.prompt import charger_prompt, formatter_prompt
from python_commun.copilot import envoyer_prompt_copilot
from python_commun.logging.logger import logger


class IaAssistantCopilotAngularReview(IaAssistantTypeReview):
    """
    Revue Angular avec Copilot.
    """

    def generer_review(self):
        prompt_template = charger_prompt("angular_review_prompt.md")
        with open(self.fichier, "r", encoding="utf-8") as f:
            code = f.read()
        prompt = formatter_prompt(
            prompt_template, code=code, version=self.version or "16"
        )
        logger.log_info("Copilot réfléchit à la revue Angular...")
        reponse = envoyer_prompt_copilot(prompt)
        logger.log_console(reponse)
