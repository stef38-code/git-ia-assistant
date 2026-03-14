#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    ia_ollama_mr_mcp - Implémentation Ollama Agentique avec MCP.

DESCRIPTION
    Cette classe implémente un agent de revue de code utilisant Ollama.
    Elle gère la boucle de "Tool Calling" manuellement en communiquant avec
    les serveurs MCP via McpClientManager.
"""

import json
import urllib.request
from pathlib import Path
from typing import Optional, List, Dict, Any
from git_ia_assistant.core.definition.ia_assistant_mr import IaAssistantMr
from python_commun.ai.mcp_client_manager import McpClientManager
from python_commun.ai.prompt import charger_prompt, formatter_prompt
from python_commun.logging import logger

OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "llama3.1" # Modèle recommandé pour le tool calling

class IaOllamaMrMcp(IaAssistantMr):
    """
    Implémentation Ollama Agentique pour la revue de Merge Request / Pull Request.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mcp_manager = None
        self.model = DEFAULT_MODEL

    def generer_revue_mr(
        self, diff_path: Optional[Path] = None, resume_path: Optional[Path] = None
    ) -> Optional[str]:
        """
        Génère une revue de la MR/PR en utilisant Ollama avec une boucle Agentique MCP.
        """
        if not self.mcp_config_path:
            logger.die("Configuration MCP manquante pour le mode Agent Ollama.")

        self.mcp_manager = McpClientManager(self.mcp_config_path)
        self.mcp_manager.demarrer_serveurs()

        try:
            # 1. Préparation des outils au format Ollama
            ollama_tools = self._preparer_outils_ollama()
            
            # 2. Préparation du prompt MCP
            prompt_template = charger_prompt(
                self._choisir_prompt_mr() + "_mcp", self.dossier_prompts
            )
            prompt = formatter_prompt(
                prompt_template,
                url=self.url_mr,
                resume="Analyse agentique en cours via Ollama...",
                liste_fichiers="Utilise l'outil git_diff pour commencer",
                langage=self.langage,
                migration_detectee="A analyser",
                migration_info="",
                numero_mr=self.numero_mr,
                version_cible=self._get_version_cible(),
            )

            messages = [{"role": "user", "content": prompt}]
            
            # 3. Boucle Agentique (max 10 itérations pour éviter les boucles infinies)
            for iteration in range(10):
                logger.log_info(f"🤖 Ollama (Itération {iteration+1}) : Réflexion...")
                
                response_data = self._appeler_ollama_chat(messages, ollama_tools)
                message = response_data.get("message", {})
                messages.append(message)

                # Si l'IA demande d'appeler des outils
                tool_calls = message.get("tool_calls", [])
                if not tool_calls:
                    # Pas d'appels d'outils -> Réponse finale
                    return message.get("content", "")

                # Exécution des outils
                for tool_call in tool_calls:
                    tool_info = tool_call.get("function", {})
                    name_full = tool_info.get("name")
                    # On retrouve le serveur et le nom de l'outil (format: serveur__outil)
                    if "__" in name_full:
                        srv_name, tool_name = name_full.split("__", 1)
                    else:
                        srv_name = "git" # Fallback
                        tool_name = name_full
                    
                    args = tool_info.get("arguments", {})
                    
                    # Exécution via le manager MCP
                    result_mcp = self.mcp_manager.executer_outil(srv_name, tool_name, args)
                    
                    # Ajout du résultat au fil de discussion
                    messages.append({
                        "role": "tool",
                        "content": json.dumps(result_mcp),
                        "tool_call_id": tool_call.get("id") # Optionnel pour Ollama mais propre
                    })

            return "Erreur : L'agent Ollama a atteint la limite d'itérations."

        except Exception as e:
            logger.log_error(f"Erreur lors de la revue Ollama MCP : {e}")
            return None
        finally:
            if self.mcp_manager:
                self.mcp_manager.arreter_serveurs()

    def _preparer_outils_ollama(self) -> List[Dict]:
        """Convertit les outils MCP en format compatible Ollama."""
        ollama_tools = []
        for tool in self.mcp_manager.get_all_tools():
            # Ollama n'aime pas les points dans les noms d'outils, on utilise __
            safe_name = f"{tool['server_name']}__{tool['name']}"
            ollama_tools.append({
                "type": "function",
                "function": {
                    "name": safe_name,
                    "description": tool.get("description", ""),
                    "parameters": tool.get("inputSchema", {"type": "object", "properties": {}})
                }
            })
        return ollama_tools

    def _appeler_ollama_chat(self, messages: List[Dict], tools: List[Dict]) -> Dict:
        """Appelle l'API /api/chat d'Ollama."""
        data = {
            "model": self.model,
            "messages": messages,
            "tools": tools,
            "stream": False
        }
        corps = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(
            OLLAMA_CHAT_URL, data=corps, headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))

    def _choisir_prompt_mr(self) -> str:
        if "angular" in self.langage.lower(): return "mr_review_angular"
        if "python" in self.langage.lower(): return "mr_review_python"
        if "java" in self.langage.lower(): return "mr_review_java"
        return "mr_review"
