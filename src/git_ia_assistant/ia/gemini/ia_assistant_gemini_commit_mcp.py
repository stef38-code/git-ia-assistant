#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from google import genai
from git_ia_assistant.core.definition.ia_assistant_commit import IaAssistantCommit
from python_commun.ai.mcp_client_manager import McpClientManager
from python_commun.ai.prompt import charger_prompt, formatter_prompt
from python_commun.logging import logger
from python_commun.system.system import detect_lang_repo

class IaAssistantGeminiCommitMcp(IaAssistantCommit):
    """
    Assistant Commit Agentique utilisant Gemini et MCP.
    """

    def generer_et_valider_commit_mcp(self):
        if not self.mcp_config_path:
            logger.die("Configuration MCP manquante.")

        mcp_manager = McpClientManager(self.mcp_config_path)
        mcp_manager.demarrer_serveurs()

        try:
            # 1. Préparation du prompt
            langage = detect_lang_repo(os.getcwd())
            prompt_template = charger_prompt("commits/commit_mcp_prompt.md", self.dossier_prompts)
            prompt = formatter_prompt(
                prompt_template,
                fichiers=", ".join(self.fichiers),
                langage=langage
            )
            
            # Instruction spécifique pour forcer le mode texte et le français
            prompt += "\n\nIMPORTANT : Génère UN SEUL message de commit au format TEXTE (pas de JSON). Rédige tout en FRANÇAIS."

            # 2. Appel Gemini
            api_key = os.getenv("GEMINI_API_KEY")
            client = genai.Client(api_key=api_key, http_options={"api_version": "v1"})
            
            logger.log_info("🤖 Gemini analyse le codebase pour le message de commit...")
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            message = response.text.strip()
            self.valider_commit(message)

        finally:
            mcp_manager.arreter_serveurs()

    def gerer_optimisation_mcp(self):
        # Pour l'optimisation, on ajoute l'instruction JSON
        if not self.mcp_config_path:
            logger.die("Configuration MCP manquante.")

        mcp_manager = McpClientManager(self.mcp_config_path)
        mcp_manager.demarrer_serveurs()

        try:
            langage = detect_lang_repo(os.getcwd())
            prompt_template = charger_prompt("commits/commit_mcp_prompt.md", self.dossier_prompts)
            prompt = formatter_prompt(
                prompt_template,
                fichiers=", ".join(self.fichiers),
                langage=langage
            )
            
            prompt += "\n\nMODE OPTIMISATION : Propose un regroupement logique au format JSON comme spécifié dans le prompt. Tout le contenu textuel à l'intérieur du JSON doit être en FRANÇAIS."

            api_key = os.getenv("GEMINI_API_KEY")
            client = genai.Client(api_key=api_key, http_options={"api_version": "v1"})
            
            logger.log_info("🤖 Gemini analyse le codebase pour optimiser les commits...")
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            # TODO: Implémenter la logique de parsing JSON et de commit groupé
            # Pour l'instant on affiche la réponse
            logger.log_console(response.text)

        finally:
            mcp_manager.arreter_serveurs()
