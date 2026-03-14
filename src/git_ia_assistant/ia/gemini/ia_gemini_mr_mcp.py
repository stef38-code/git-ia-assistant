#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pathlib import Path
from typing import Optional
from google import genai
from git_ia_assistant.core.definition.ia_assistant_mr import IaAssistantMr
from python_commun.ai.mcp_client_manager import McpClientManager
from python_commun.ai.prompt import charger_prompt, formatter_prompt
from python_commun.logging import logger

class IaGeminiMrMcp(IaAssistantMr):
    """
    Implémentation Agentique de Gemini utilisant les serveurs MCP.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mcp_manager = None

    def generer_revue_mr(self, diff_path: Optional[Path] = None, resume_path: Optional[Path] = None) -> Optional[str]:
        """
        Génère une revue de la MR/PR en utilisant Google Gemini en mode Agent MCP.
        """
        if not self.mcp_config_path:
            logger.die("Configuration MCP manquante pour le mode Agent Gemini.")

        # Démarrage des serveurs MCP
        self.mcp_manager = McpClientManager(self.mcp_config_path)
        self.mcp_manager.demarrer_serveurs()

        try:
            # 1. Préparation du prompt MCP
            # On utilise le prompt spécifique au langage si possible
            nom_base_prompt = self._choisir_prompt_mr()
            prompt_name = f"{nom_base_prompt}_mcp"
            
            prompt_template = charger_prompt(prompt_name, self.dossier_prompts)
            
            # En mode Agent, on ne passe pas le diff complet pour économiser les tokens
            prompt = formatter_prompt(
                prompt_template,
                url=self.url_mr,
                resume="Analyse agentique en cours via outils MCP...",
                liste_fichiers="Utilise l'outil git.git_diff pour identifier les changements.",
                langage=self.langage,
                migration_detectee="À vérifier via outils",
                migration_info="L'IA doit explorer le code pour détecter les changements de version.",
                numero_mr=self.numero_mr,
                version_cible=self._get_version_cible()
            )

            # 2. Configuration du client Gemini
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                logger.die("La variable d'environnement GEMINI_API_KEY n'est pas configurée.")
                
            client = genai.Client(api_key=api_key, http_options={"api_version": "v1alpha"})
            
            # 3. Exécution de l'Agent
            logger.log_info("🤖 Gemini (Agent MCP) analyse le dépôt...")
            
            # Note: Pour une boucle de tool-calling complète, il faudrait itérer ici.
            # Pour l'instant, nous envoyons le prompt d'investigation.
            response = client.models.generate_content(
                model="auto",
                contents=prompt
            )
            
            return response.text.strip() if hasattr(response, "text") else str(response).strip()

        except Exception as e:
            logger.log_error(f"Erreur lors de la génération de la revue Gemini MCP : {e}")
            return None
        finally:
            if self.mcp_manager:
                try:
                    self.mcp_manager.arreter_serveurs()
                except Exception:
                    pass

    def _choisir_prompt_mr(self) -> str:
        """Choisit le nom du prompt en fonction du langage détecté."""
        lang = self.langage.lower()
        if "angular" in lang:
            return "mr_review_angular"
        elif "python" in lang:
            return "mr_review_python"
        elif "java" in lang:
            return "mr_review_java"
        return "mr_review"
