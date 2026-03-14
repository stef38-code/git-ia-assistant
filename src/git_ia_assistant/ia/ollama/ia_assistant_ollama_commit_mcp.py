#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import urllib.request
from git_ia_assistant.core.definition.ia_assistant_commit import IaAssistantCommit
from python_commun.ai.mcp_client_manager import McpClientManager
from python_commun.ai.prompt import charger_prompt, formatter_prompt
from python_commun.logging import logger
from python_commun.system.system import detect_lang_repo

OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "llama3.1"

class IaAssistantOllamaCommitMcp(IaAssistantCommit):
    """
    Assistant Commit Agentique utilisant Ollama et MCP.
    """

    def generer_et_valider_commit_mcp(self):
        if not self.mcp_config_path:
            logger.die("Configuration MCP manquante.")

        mcp_manager = McpClientManager(self.mcp_config_path)
        mcp_manager.demarrer_serveurs()

        try:
            ollama_tools = self._preparer_outils_ollama(mcp_manager)
            prompt_template = charger_prompt("commits/commit_mcp_prompt.md", self.dossier_prompts)
            prompt = formatter_prompt(
                prompt_template,
                fichiers=", ".join(self.fichiers),
                langage=detect_lang_repo(os.getcwd())
            )

            messages = [{"role": "user", "content": prompt}]
            
            for iteration in range(10):
                logger.log_info(f"🤖 Ollama (Itération {iteration+1}) : Analyse...")
                response_data = self._appeler_ollama_chat(messages, ollama_tools)
                message_obj = response_data.get("message", {})
                messages.append(message_obj)

                tool_calls = message_obj.get("tool_calls", [])
                if not tool_calls:
                    final_message = message_obj.get("content", "").strip()
                    self.valider_commit(final_message)
                    return

                for tool_call in tool_calls:
                    tool_info = tool_call.get("function", {})
                    name_full = tool_info.get("name")
                    srv_name, tool_name = name_full.split("__", 1) if "__" in name_full else ("git", name_full)
                    
                    result_mcp = mcp_manager.executer_outil(srv_name, tool_name, tool_info.get("arguments", {}))
                    messages.append({"role": "tool", "content": json.dumps(result_mcp)})

        finally:
            mcp_manager.arreter_serveurs()

    def _preparer_outils_ollama(self, mcp_manager) -> list:
        tools = []
        for tool in mcp_manager.get_all_tools():
            tools.append({
                "type": "function",
                "function": {
                    "name": f"{tool['server_name']}__{tool['name']}",
                    "description": tool.get("description", ""),
                    "parameters": tool.get("inputSchema", {"type": "object", "properties": {}})
                }
            })
        return tools

    def _appeler_ollama_chat(self, messages, tools) -> dict:
        data = {"model": DEFAULT_MODEL, "messages": messages, "tools": tools, "stream": False}
        req = urllib.request.Request(OLLAMA_CHAT_URL, data=json.dumps(data).encode("utf-8"), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))

    def gerer_optimisation_mcp(self):
        self.generer_et_valider_commit_mcp()
