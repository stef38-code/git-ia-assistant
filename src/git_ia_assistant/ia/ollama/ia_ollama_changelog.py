#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Classe pour la génération de changelog IA avec Ollama.
"""

from git_ia_assistant.definition.ia_assistant_changelog import IaAssistantChangelog
from python_commun.prompt import charger_prompt, formatter_prompt
from python_commun.ollama_utils import envoyer_prompt_ollama
from python_commun.logging.logger import logger


class IaOllamaChangelog(IaAssistantChangelog):
    """
    Génération de changelog IA via Ollama.
    """

    def recuperer_commits(self):
        return list(self.repo.iter_commits("HEAD", max_count=int(self.limite)))

    def generer_prompt(self, messages):
        prompt = "Changelog pour les commits suivants :\n"
        for commit in messages:
            prompt += f"- {commit.hexsha[:7]}: {commit.summary}\n"
        return prompt

    def generer_changelog(self, messages):
        modele_prompt = charger_prompt("changelog_prompt.md")
        texte_commits = "\n".join(
            f"- {commit.hexsha[:7]}: {commit.summary}" for commit in messages
        )
        prompt_final = formatter_prompt(modele_prompt, commits=texte_commits)
        logger.log_info("Ollama génère le changelog...")
        return envoyer_prompt_ollama(prompt_final)
