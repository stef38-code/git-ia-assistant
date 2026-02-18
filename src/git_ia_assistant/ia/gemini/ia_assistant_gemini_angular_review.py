#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Revue Angular avec Gemini.
Exemple :
    review = IaAssistantGeminiAngularReview('monfichier.ts', version='16')
    review.generer_review()
"""

from git_ia_assistant.definition.ia_assistant_type_review import IaAssistantTypeReview
from python_commun.prompt import charger_prompt, formatter_prompt
from python_commun import gemini_utils, logger


class IaAssistantGeminiAngularReview(IaAssistantTypeReview):
    """
    Revue Angular avec Gemini.
    """

    def generer_review(self):
        prompt_template = charger_prompt("angular_review_prompt.md")
        with open(self.fichier, "r", encoding="utf-8") as f:
            code = f.read()
        prompt = formatter_prompt(
            prompt_template, code=code, version=self.version or "16"
        )
        logger.log_info("Gemini réfléchit à la revue Angular...")
        model = gemini_utils.configurer_gemini()
        reponse = model.models.generate_content(
            model=gemini_utils.MODEL_NAME, contents=prompt
        )
        logger.log_console(reponse.text)
