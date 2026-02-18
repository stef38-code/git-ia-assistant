#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    ia_ollama_squash - Suggestion de squash IA avec Ollama

DESCRIPTION
    Classe pour générer une suggestion de squash de commits via Ollama.

FUNCTIONS
    recuperer_commits() -> list
        Récupère les derniers commits à traiter.
    generer_prompt(commits: list) -> str
        Génère le prompt détaillé pour Ollama avec la liste des commits.
    generer_squash(commits: list) -> str
        Envoie le prompt à Ollama et retourne la suggestion de squash.

DATA
    Aucune
"""

from git_ia_assistant.core.definition.ia_assistant_squash import IaAssistantSquash
from python_commun.ai.prompt import charger_prompt, formatter_prompt
from python_commun.ai.ollama_utils import envoyer_prompt_ollama
from python_commun.logging.logger import logger


class IaOllamaSquash(IaAssistantSquash):
    """
    Suggestion de squash IA via Ollama.
    """

    def recuperer_commits(self) -> list:
        """
        Récupère les derniers commits à traiter.
        :return: Liste des commits Git
        """
        return list(self.repo.iter_commits("HEAD", max_count=self.nb_commits))

    def generer_prompt(self, liste_commits: list) -> str:
        """
        Génère le prompt détaillé pour Ollama avec la liste des commits.
        :param liste_commits: Liste des commits à traiter
        :return: Prompt textuel détaillé
        """
        return self.generer_prompt_squash(liste_commits)

    def generer_squash(self, liste_commits: list) -> str:
        """
        Envoie le prompt à Ollama et retourne la suggestion de squash.
        :param liste_commits: Liste des commits à traiter
        :return: Suggestion textuelle générée par Ollama
        """
        modele_prompt = charger_prompt("squash_prompt.md")
        texte_commits = self.formatter_liste_commits(liste_commits)
        prompt_final = formatter_prompt(modele_prompt, commits=texte_commits)
        logger.log_info("Ollama réfléchit à la stratégie de squash...")
        return envoyer_prompt_ollama(prompt_final)
