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

            # 2. Appel Gemini
            api_key = os.getenv("GEMINI_API_KEY")
            client = genai.Client(api_key=api_key, http_options={"api_version": "v1beta"})
            
            logger.log_info("🤖 Gemini analyse le codebase pour le message de commit...")
            response = client.models.generate_content(
                model="gemini-3-pro-preview",
                contents=prompt
            )
            
            message = response.text.strip()
            self.valider_commit(message)

        finally:
            mcp_manager.arreter_serveurs()

    def gerer_optimisation_mcp(self):
        # Logique d'optimisation JSON (similaire mais avec boucle tool calling pour plus de précision)
        # Pour une V1 MCP, on garde la structure simple
        self.generer_et_valider_commit_mcp()
