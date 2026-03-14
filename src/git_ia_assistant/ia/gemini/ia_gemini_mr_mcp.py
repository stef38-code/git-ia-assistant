#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
from typing import Optional
from git_ia_assistant.core.definition.ia_assistant_mr import IaAssistantMr
from python_commun.ai.mcp_client_manager import McpClientManager
from python_commun.ai.prompt import charger_prompt, formatter_prompt
from python_commun.logging import logger
import os
from google import genai
from google.genai import types

class IaGeminiMrMcp(IaAssistantMr):
    """
    Implémentation Agentique de Gemini utilisant les serveurs MCP.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mcp_manager = None

    def generer_revue_mr(self, diff_path: Optional[Path] = None, resume_path: Optional[Path] = None) -> Optional[str]:
        if not self.mcp_config_path:
            logger.die("Configuration MCP manquante pour le mode Agent.")

        self.mcp_manager = McpClientManager(self.mcp_config_path)
        self.mcp_manager.demarrer_serveurs()

        try:
            # Préparation du prompt (léger car sans diff)
            prompt_template = charger_prompt(self._choisir_prompt_mr() + "_mcp", self.dossier_prompts)
            
            # Récupération des fichiers modifiés (on pourrait aussi laisser l'IA le faire)
            liste_fichiers = "Consultable via git.git_diff"
            
            prompt = formatter_prompt(
                prompt_template,
                url=self.url_mr,
                resume="Analyse en cours via outils...",
                liste_fichiers=liste_fichiers,
                langage=self.langage,
                migration_detectee="A vérifier via outils",
                migration_info="",
                numero_mr=self.numero_mr,
                version_cible=self._get_version_cible()
            )

            # Configuration du client Gemini avec les outils MCP
            api_key = os.getenv("GEMINI_API_KEY")
            client = genai.Client(api_key=api_key, http_options={"api_version": "v1"})
            
            # Conversion des outils MCP en outils Gemini
            gemini_tools = []
            for tool in self.mcp_manager.get_all_tools():
                # On simplifie ici, une vraie conversion nécessiterait de mapper les types JSON Schema
                # Pour cet exemple, on suppose que l'IA sait appeler les fonctions par leur nom
                pass

            # Boucle de réflexion (Agent)
            # Note: Le SDK google-genai gère automatiquement le tool calling si on passe tools=[]
            # Mais ici nous devons faire le pont manuellement avec nos serveurs MCP.
            
            logger.log_info("🤖 Envoi du prompt à Gemini (Mode Agent)...")
            # Appel simplifié (pour une implémentation complète, il faudrait gérer l'itération tools)
            response = client.models.generate_content(
                model="gemini-2.0-flash", # Modèle supportant bien les outils
                contents=prompt
            )
            
            return response.text

        finally:
            if self.mcp_manager:
                self.mcp_manager.arreter_serveurs()

    def _choisir_prompt_mr(self) -> str:
        # Logique pour choisir le prompt selon le langage
        if "angular" in self.langage.lower(): return "mr_review_angular"
        if "python" in self.langage.lower(): return "mr_review_python"
        if "java" in self.langage.lower(): return "mr_review_java"
        return "mr_review"
