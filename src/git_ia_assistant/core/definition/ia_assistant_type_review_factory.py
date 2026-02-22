#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    ia_assistant_type_review_factory - Factory pour instancier les classes de revue de code par type de langage et IA.

DESCRIPTION
    Cette factory est chargée de retourner la classe de revue de code IA
    appropriée en fonction de l'IA sélectionnée (Copilot, Gemini, Ollama)
    et du langage de programmation du projet (Angular, Python, Java, etc.).
    Elle gère l'importation dynamique des classes spécifiques pour éviter
    les dépendances circulaires et centralise la logique de sélection.

FUNCTIONS
    get_review_class(ia, type_lang) -> Type[IaAssistantTypeReview] | None
        Retourne la classe de revue de code IA correspondant à l'IA et au langage.
    create_review_instance(ia, type_lang, fichiers, version, repo_path) -> IaAssistantTypeReview | None
        Crée une instance de la classe de revue de code appropriée.

DATA
    Aucune.
"""


class IaAssistantTypeReviewFactory:
    @classmethod
    def get_review_class(cls, ia, type_lang):
        # Logique pour retourner la bonne classe selon l'IA et le langage
        if ia == "copilot" and type_lang == "angular":
            from git_ia_assistant.ia.copilot.ia_assistant_copilot_angular_review import (
                IaAssistantCopilotAngularReview,
            )

            return IaAssistantCopilotAngularReview
        if ia == "gemini" and type_lang == "angular":
            from git_ia_assistant.ia.gemini.ia_assistant_gemini_angular_review import (
                IaAssistantGeminiAngularReview,
            )

            return IaAssistantGeminiAngularReview
        if ia == "copilot" and type_lang == "python":
            from git_ia_assistant.ia.copilot.ia_assistant_copilot_python_review import (
                IaAssistantCopilotPythonReview,
            )

            return IaAssistantCopilotPythonReview
        if ia == "gemini" and type_lang == "python":
            from git_ia_assistant.ia.gemini.ia_assistant_gemini_python_review import (
                IaAssistantGeminiPythonReview,
            )

            return IaAssistantGeminiPythonReview
        if ia == "ollama" and type_lang == "python":
            from git_ia_assistant.ia.ollama.ia_assistant_ollama_python_review import (
                IaAssistantOllamaPythonReview,
            )

            return IaAssistantOllamaPythonReview
        # Ajouter les autres cas
        from python_commun.logging.logger import logger

        logger.log_warn(
            f"Le langage '{type_lang}' n'est pas supporté pour la review avec l'IA '{ia}'. Aucun prompt ne sera généré."
        )
        return None

    @classmethod
    def create_review_instance(cls, ia, type_lang, fichiers, version, repo_path):
        review_cls = cls.get_review_class(ia, type_lang)
        return review_cls(fichiers, version, repo_path)
