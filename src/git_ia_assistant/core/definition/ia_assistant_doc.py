#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    ia_assistant_doc - Classe mère pour la génération de documentation IA.
"""

import os
from git_ia_assistant.core.definition.ia_assistant import IaAssistant
from python_commun.ai.prompt import charger_prompt, formatter_prompt
from python_commun.system.system import detect_lang_repo

class IaAssistantDoc(IaAssistant):
    """
    Classe de base pour générer de la documentation avec l'IA.
    """

    def __init__(self, fichier: str, doc_format: str = None, langue: str = "Français"):
        super().__init__()
        self.fichier = fichier
        self.doc_format = doc_format
        self.langue = langue

    def generer_prompt(self) -> str:
        """
        Génère le prompt pour la documentation.
        """
        with open(self.fichier, "r", encoding="utf-8") as f:
            code = f.read()
        
        langage = detect_lang_repo(os.path.dirname(self.fichier))
        
        if not self.doc_format:
            if langage == "python":
                self.doc_format = "Docstrings Python"
            elif langage == "java":
                self.doc_format = "Javadoc"
            else:
                self.doc_format = "Markdown"

        template = charger_prompt("doc_generation_prompt.md", self.dossier_prompts)
        return formatter_prompt(
            template,
            code=code,
            doc_format=self.doc_format,
            langue=self.langue
        )

    def generer_doc(self) -> str:
        """
        Méthode abstraite.
        """
        raise NotImplementedError
