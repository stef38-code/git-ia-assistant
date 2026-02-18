#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Revue Python avec Ollama.
Exemple :
    review = IaAssistantOllamaPythonReview('monfichier.py', version='3.10')
    review.generer_review()
"""

from git_ia_assistant.definition.ia_assistant_type_review import IaAssistantTypeReview
from python_commun.prompt import charger_prompt, formatter_prompt
from python_commun.logging.logger import logger
from git_ia_assistant.ollama import ollama_utils


class IaAssistantOllamaPythonReview(IaAssistantTypeReview):
    """
    Revue Python avec Ollama.
    """

    def generer_review(self):
        prompt_template = charger_prompt("python_review_prompt.md")
        with open(self.fichiers[0], "r", encoding="utf-8") as f:
            code = f.read()
        prompt = formatter_prompt(
            prompt_template, code=code, version=self.version or "3.x"
        )
        logger.log_info("Ollama réfléchit à la revue Python...")
        reponse = ollama_utils.appeler_ollama(prompt, modele="llama3.1")
        logger.log_console(reponse)

    def generer_prompt_review(self):
        prompt_template = charger_prompt("python_review_prompt.md")
        with open(self.fichiers[0], "r", encoding="utf-8") as f:
            code = f.read()
        prompt = formatter_prompt(
            prompt_template, code=code, version=self.version or "3.x"
        )
        return prompt
