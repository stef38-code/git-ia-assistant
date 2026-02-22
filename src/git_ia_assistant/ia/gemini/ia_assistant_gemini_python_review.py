#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Revue Python avec Gemini.
Exemple :
    review = IaAssistantGeminiPythonReview('monfichier.py', version='3.10')
    review.generer_review()
"""

from git_ia_assistant.core.definition.ia_assistant_type_review import IaAssistantTypeReview
from python_commun.ai.prompt import charger_prompt, formatter_prompt
from python_commun.ai import gemini_utils
from python_commun.logging.logger import logger


class IaAssistantGeminiPythonReview(IaAssistantTypeReview):
    """
    Revue Python avec Gemini.
    """

    def generer_review(self):
        prompt_template = charger_prompt("python_review_prompt.md", self.dossier_prompts)
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
        if not self.fichiers:
            return ""
        
        chemin_fichier = self.fichiers[0]
        with open(chemin_fichier, "r", encoding="utf-8") as f:
            code = f.read()

        contexte_imports = self._extraire_contexte_imports(chemin_fichier, code)
        
        prompt_template = charger_prompt("python_review_prompt.md", self.dossier_prompts)
        prompt = formatter_prompt(
            prompt_template, code=code, version=self.version or "3.x"
        )
        
        if contexte_imports:
            prompt += f"\n\nCONTEXTE SUPPLÉMENTAIRE (fichiers importés) :\n{contexte_imports}"
            
        return prompt
