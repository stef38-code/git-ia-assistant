#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from git_ia_assistant.core.definition.ia_assistant_commit import IaAssistantCommit
from python_commun.ai.copilot import envoyer_prompt_copilot
from python_commun.ai.prompt import charger_prompt, formatter_prompt
from python_commun.logging import logger
from python_commun.system.system import detect_lang_repo

class IaAssistantCopilotCommitMcp(IaAssistantCommit):
    """
    Assistant Commit Agentique utilisant Copilot et MCP.
    """

    def generer_et_valider_commit_mcp(self):
        prompt_template = charger_prompt("commits/commit_mcp_prompt.md", self.dossier_prompts)
        prompt = formatter_prompt(
            prompt_template,
            fichiers=", ".join(self.fichiers),
            langage=detect_lang_repo(os.getcwd())
        )

        logger.log_info("🤖 Copilot analyse le codebase (MCP) pour le message de commit...")
        message = envoyer_prompt_copilot(prompt, mcp_config_path=self.mcp_config_path)
        
        # Nettoyage : extraire le bloc Conventional Commit si présent
        import re
        commit_pattern = re.compile(r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\(.*\))?!?:", re.IGNORECASE)
        lines = message.splitlines()
        start_index = -1
        for i, line in enumerate(lines):
            if commit_pattern.match(line.strip()):
                start_index = i
                break
        if start_index != -1:
            message = "\n".join(lines[start_index:]).strip()

        self.valider_commit(message)

    def gerer_optimisation_mcp(self):
        self.generer_et_valider_commit_mcp()
