#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Classe commit pour l'IA Gemini.
"""

from git_ia_assistant.core.definition.ia_assistant_commit import IaAssistantCommit


class IaAssistantGeminiCommit(IaAssistantCommit):
    """
    Implémentation de la génération de message de commit via Gemini.
    """
    def _envoyer_prompt_ia(self, prompt: str) -> str:
        """
        Envoie le prompt à l'API Gemini et retourne la réponse.

        :param prompt: Le prompt à envoyer.
        :return: La réponse texte de l'IA.
        """
        # Assurez-vous que le chemin d'import est correct pour votre structure
        from python_commun.ai.gemini_utils import envoyer_prompt_gemini

        return envoyer_prompt_gemini(prompt)
