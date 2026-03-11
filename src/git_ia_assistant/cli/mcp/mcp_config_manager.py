#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    mcp_config_manager - Gestionnaire de configuration dynamique pour serveurs MCP.

DESCRIPTION
    Ce module permet de générer un fichier de configuration JSON compatible MCP
    en fonction du contexte de la revue de code (plateforme, langage détecté).
    Il est particulièrement utile pour l'option --additional-mcp-config de Copilot CLI.

FUNCTIONS
    generer_mcp_config(out_dir, plateforme, langage, ...) -> Optional[Path]
"""

import json
import os
from pathlib import Path
from typing import Optional
from python_commun.logging import logger

# Définition des serveurs MCP disponibles
SERVEURS = {
    "git": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-git"]
    },
    "github": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "env_var": "GITHUB_PERSONAL_ACCESS_TOKEN" # On utilise GIT_TOKEN par défaut ou celui-ci
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
        # Note: Utilisation d'un serveur de doc si serveur spécifique non dispo
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-angular"] 
    },
    "sonarqube": {
        "command": "npx",
        "args": ["-y", "mcp-server-sonarqube"],
        "env_var": "SONAR_TOKEN"
    }
}

class McpConfigManager:
    """
    Gère la création et la persistance de la configuration MCP.
    """

    @staticmethod
    def generer_config(
        out_dir: Path,
        plateforme: str,
        langage: str,
        token: Optional[str] = None
    ) -> Optional[Path]:
        """
        Génère un fichier mcp-config.json adapté au contexte.

        :param out_dir: Répertoire de sortie pour le fichier JSON.
        :param plateforme: 'github' ou 'gitlab'.
        :param langage: Langage détecté (ex: 'Angular', 'Python').
        :param token: Token d'accès (sera utilisé pour GitHub/GitLab).
        :return: Chemin vers le fichier généré ou None si échec.
        """
        config = {"mcpServers": {}}
        langage_lower = langage.lower()

    # 1. Git (Toujours inclus)
        config["mcpServers"]["git"] = SERVEURS["git"]

    # 2. Plateforme spécifique
        if plateforme.lower() == "github":
            config["mcpServers"]["github"] = SERVEURS["github"]
            # Injection du token dans l'environnement du serveur MCP
            if token:
                config["mcpServers"]["github"]["env"] = {"GITHUB_PERSONAL_ACCESS_TOKEN": token}
        elif plateforme.lower() == "gitlab":
            config["mcpServers"]["gitlab"] = SERVEURS["gitlab"]
            if token:
                config["mcpServers"]["gitlab"]["env"] = {"GITLAB_PRIVATE_TOKEN": token}

    # 3. Sequential Thinking (Toujours inclus pour la qualité du raisonnement)
        config["mcpServers"]["sequential-thinking"] = SERVEURS["sequential-thinking"]

    # 4. Langage spécifique (Angular / TypeScript)
        is_ts = "typescript" in langage_lower or "angular" in langage_lower
        if is_ts:
            config["mcpServers"]["typescript"] = SERVEURS["typescript"]
        
        if "angular" in langage_lower:
            config["mcpServers"]["angular"] = SERVEURS["angular"]

    # 5. SonarQube (Inclus si SONAR_TOKEN est présent dans l'environnement)
        sonar_token = os.environ.get("SONAR_TOKEN")
        if sonar_token:
            config["mcpServers"]["sonarqube"] = SERVEURS["sonarqube"]
            config["mcpServers"]["sonarqube"]["env"] = {"SONAR_TOKEN": sonar_token}

        # Sauvegarde du fichier
        config_path = out_dir / "mcp-config.json"
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
            logger.log_info(f"Configuration MCP générée : {config_path}")
            return config_path
        except Exception as e:
            logger.log_error(f"Erreur lors de la génération de mcp-config.json : {e}")
            return None
