#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from pathlib import Path
from typing import Optional
from python_commun.logging import logger

SERVEURS = {
    "git": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-git"]
    },
    "github": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "env_var": "GITHUB_PERSONAL_ACCESS_TOKEN"
    },
    "gitlab": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-gitlab"],
        "env_var": "GITLAB_PRIVATE_TOKEN"
    },
    "sequential-thinking": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    },
    "typescript": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-typescript"]
    },
    "angular": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-angular"]
    },
    "sonarqube": {
        "command": "npx",
        "args": ["-y", "mcp-server-sonarqube"],
        "env_var": "SONAR_TOKEN"
    },
    "filesystem": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem"]
    },
    "search": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-ripgrep"]
    }
}

class McpConfigManager:
    @staticmethod
    def generer_config(out_dir, plateforme, langage, token=None, repo_path=None):
        config = {"mcpServers": {}}
        langage_lower = langage.lower()
        config["mcpServers"]["git"] = SERVEURS["git"]
        if plateforme.lower() == "github":
            config["mcpServers"]["github"] = SERVEURS["github"].copy()
            if token: config["mcpServers"]["github"]["env"] = {"GITHUB_PERSONAL_ACCESS_TOKEN": token}
        elif plateforme.lower() == "gitlab":
            config["mcpServers"]["gitlab"] = SERVEURS["gitlab"].copy()
            if token: config["mcpServers"]["gitlab"]["env"] = {"GITLAB_PRIVATE_TOKEN": token}
        config["mcpServers"]["sequential-thinking"] = SERVEURS["sequential-thinking"]
        if "typescript" in langage_lower or "angular" in langage_lower:
            config["mcpServers"]["typescript"] = SERVEURS["typescript"]
        if "angular" in langage_lower:
            config["mcpServers"]["angular"] = SERVEURS["angular"]
        sonar_token = os.environ.get("SONAR_TOKEN")
        if sonar_token:
            config["mcpServers"]["sonarqube"] = SERVEURS["sonarqube"].copy()
            config["mcpServers"]["sonarqube"]["env"] = {"SONAR_TOKEN": sonar_token}
        if repo_path:
            config["mcpServers"]["filesystem"] = {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", str(repo_path)]
            }
            config["mcpServers"]["search"] = {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-ripgrep", "--directory", str(repo_path)]
            }
        config_path = Path(out_dir) / "mcp-config.json"
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
            logger.log_info(f"Configuration MCP générée : {config_path}")
            return config_path
        except Exception as e:
            logger.log_error(f"Erreur lors de la génération de mcp-config.json : {e}")
            return None
