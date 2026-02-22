#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    ia_assistant_test - Classe mère pour la génération de tests IA.
"""

import os
from git_ia_assistant.core.definition.ia_assistant import IaAssistant
from python_commun.ai.prompt import charger_prompt, formatter_prompt
from python_commun.system.system import detect_lang_repo

class IaAssistantTest(IaAssistant):
    """
    Classe de base pour générer des tests avec l'IA.
    """

    def __init__(self, fichier: str, test_framework: str = None, test_type: str = "unit"):
        super().__init__()
        self.fichier = fichier
        self.test_framework = test_framework
        self.test_type = test_type

    def generer_prompt(self, framework_version: str = "latest") -> str:
        """
        Génère le prompt pour la génération de tests.
        """
        with open(self.fichier, "r", encoding="utf-8") as f:
            code = f.read()
        
        langage = detect_lang_repo(os.path.dirname(self.fichier))
        
        # Définit le framework par défaut si non spécifié
        if not self.test_framework:
            if langage == "python":
                self.test_framework = "PyTest"
            elif langage == "java":
                self.test_framework = "JUnit/Mockito/AssertJ"
            elif langage == "angular":
                self.test_framework = "Jasmine/Jest"
            else:
                self.test_framework = "Generic"

        # Instructions spécifiques
        framework_instructions = self._get_framework_instructions()

        template = charger_prompt("test_generation_prompt.md", self.dossier_prompts)
        return formatter_prompt(
            template,
            code=code,
            langage=langage,
            test_framework=self.test_framework,
            framework_version=framework_version,
            test_type=self.test_type,
            framework_instructions=framework_instructions
        )

    def _get_framework_instructions(self) -> str:
        """
        Retourne des instructions spécifiques selon le framework.
        """
        instructions = {
            "PyTest": "- Utilise `pytest`. Préfère les `fixtures` aux classes `unittest`. Utilise `pytest-mock` si nécessaire.",
            "JUnit/Mockito/AssertJ": "- Utilise `JUnit 5`. Mocke les dépendances avec `@Mock`. Utilise les assertions fluides de `AssertJ` (`assertThat`).",
            "Jasmine/Jest": "- Utilise la syntaxe `describe/it/expect`. Préfère les mocks de Jest (`jest.fn()`).",
            "Vitest": "- Utilise la syntaxe Vitest (proche de Jest). Inclus les imports de `vitest`.",
            "Playwright": "- Génère un test de bout en bout (E2E). Utilise `page.goto`, `page.click`, et les assertions `expect(page).to_have_title`.",
        }
        return instructions.get(self.test_framework, "- Suivre les standards de test pour le langage spécifié.")

    def generer_tests(self) -> str:
        """
        Méthode abstraite à implémenter.
        """
        raise NotImplementedError
