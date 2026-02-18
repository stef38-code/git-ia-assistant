#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Revue Python avec Gemini.
Exemple :
    review = IaAssistantGeminiPythonReview('monfichier.py', version='3.10')
    review.generer_review()
"""

from git_ia_assistant.definition.ia_assistant_type_review import IaAssistantTypeReview
from python_commun.prompt import charger_prompt, formatter_prompt
from python_commun import gemini_utils, logger


class IaAssistantGeminiPythonReview(IaAssistantTypeReview):
    """
    Revue Python avec Gemini.
    """

    def generer_review(self):
        prompt_template = charger_prompt("python_review_prompt.md")
        with open(self.fichiers[0], "r", encoding="utf-8") as f:
            code = f.read()
        prompt = formatter_prompt(
            prompt_template, code=code, version=self.version or "3.x"
        )
        logger.log_info("Gemini réfléchit à la revue Python...")
        model = gemini_utils.configurer_gemini()
        reponse = model.models.generate_content(
            model=gemini_utils.MODEL_NAME, contents=prompt
        )
        logger.log_console(reponse.text)

    def generer_prompt_review(self):
        prompt_template = charger_prompt("python_review_prompt.md")
        with open(self.fichiers[0], "r", encoding="utf-8") as f:
            code = f.read()
        prompt = formatter_prompt(
            prompt_template, code=code, version=self.version or "3.x"
        )
        return prompt
