#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Revue Java avec Ollama.
Exemple :
    review = IaAssistantOllamaJavaReview('monfichier.java', version='17')
    review.generer_review()
"""

from git_ia_assistant.definition.ia_assistant_type_review import IaAssistantTypeReview
from python_commun.prompt import charger_prompt, formatter_prompt
from python_commun.logging.logger import logger
from git_ia_assistant.ollama import ollama_utils


class IaAssistantOllamaJavaReview(IaAssistantTypeReview):
    """
    Revue Java avec Ollama.
    """

    def generer_review(self):
        prompt_template = charger_prompt("java_review_prompt.md")
        with open(self.fichier, "r", encoding="utf-8") as f:
            code = f.read()
        prompt = formatter_prompt(
            prompt_template, code=code, version=self.version or "17"
        )
        logger.log_info("Ollama réfléchit à la revue Java...")
        reponse = ollama_utils.appeler_ollama(prompt, modele="llama3.1")
        logger.log_console(reponse)
