#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional
from python_commun.logging import logger

# Instructions d'installation pour chaque serveur MCP
INSTALLATION_INSTRUCTIONS = {
    "mcp-server-git": (
        "pip install mcp-server-git\n"
        "  ou via uvx (sans installation) : uvx mcp-server-git\n"
        "  ⚠️  Requiert Python ≥ 3.10 et uv : https://docs.astral.sh/uv/"
    ),
    "@modelcontextprotocol/server-github": (
        "npm install -g @modelcontextprotocol/server-github\n"
        "  ⚠️  Requiert la variable d'environnement : GITHUB_PERSONAL_ACCESS_TOKEN\n"
        "  ou via npx : npx -y @modelcontextprotocol/server-github"
    ),
    "@modelcontextprotocol/server-gitlab": (
        "npm install -g @modelcontextprotocol/server-gitlab\n"
        "  ⚠️  Requiert la variable d'environnement : GITLAB_PRIVATE_TOKEN\n"
        "  ou via npx : npx -y @modelcontextprotocol/server-gitlab"
    ),
    "@modelcontextprotocol/server-sequential-thinking": (
        "npm install -g @modelcontextprotocol/server-sequential-thinking\n"
        "  ou via npx : npx -y @modelcontextprotocol/server-sequential-thinking"
    ),
    "@modelcontextprotocol/server-typescript": (
        "npm install -g @modelcontextprotocol/server-typescript\n"
        "  ou via npx : npx -y @modelcontextprotocol/server-typescript"
    ),
    "@modelcontextprotocol/server-angular": (
        "npm install -g @modelcontextprotocol/server-angular\n"
        "  ou via npx : npx -y @modelcontextprotocol/server-angular"
    ),
    "mcp-server-sonarqube": (
        "npm install -g mcp-server-sonarqube\n"
        "  ⚠️  Requiert la variable d'environnement : SONAR_TOKEN\n"
        "  ou via npx : npx -y mcp-server-sonarqube"
    ),
    "@modelcontextprotocol/server-filesystem": (
        "npm install -g @modelcontextprotocol/server-filesystem\n"
        "  ou via npx : npx -y @modelcontextprotocol/server-filesystem"
    ),
    "@modelcontextprotocol/server-ripgrep": (
        "npm install -g @modelcontextprotocol/server-ripgrep\n"
        "  ou via npx : npx -y @modelcontextprotocol/server-ripgrep"
    ),
}

SERVEURS = {
    "git": {
        "command": "uvx",
        "args": ["mcp-server-git"]
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
    def verifier_installation(servers: Optional[list] = None) -> bool:
        """
        Vérifie que les serveurs MCP requis sont accessibles.

        Contrôles effectués :
        - présence des lanceurs (``npx``/``node`` pour npm, ``uvx`` pour Python)
        - disponibilité de chaque package selon son gestionnaire
        - présence des variables d'environnement requises

        Parameters
        ----------
        servers:
            Liste de clés de ``SERVEURS`` à vérifier.
            Si ``None``, vérifie tous les serveurs présents dans ``SERVEURS``.

        Returns
        -------
        bool
            ``True`` si tout est correct, ``False`` si au moins un problème a été détecté.
        """
        ok = True
        border = "─" * 60
        selection = {k: v for k, v in SERVEURS.items() if servers is None or k in servers}

        # Sépare les serveurs selon leur lanceur
        npm_servers  = {server_name: server_config for server_name, server_config in selection.items() if server_config["command"] == "npx"}
        uvx_servers  = {server_name: server_config for server_name, server_config in selection.items() if server_config["command"] == "uvx"}

        manquants = []

        # ── NPM / npx ────────────────────────────────────────────────────────
        if npm_servers:
            if not shutil.which("npx") or not shutil.which("node"):
                for k, srv in npm_servers.items():
                    pkg = srv["args"][1] if srv.get("args") else k
                    manquants.append(pkg)
                logger.log_error(
                    "Node.js / npx est introuvable dans le PATH.\n"
                    "  Installez Node.js (≥ 18) : https://nodejs.org"
                )
            else:
                # Liste des packages installés globalement (une seule commande)
                try:
                    result = subprocess.run(
                        ["npm", "list", "-g", "--depth=0", "--json"],
                        capture_output=True, text=True, timeout=15
                    )
                    global_pkgs: dict = json.loads(result.stdout).get("dependencies", {}) if result.stdout else {}
                except Exception:
                    global_pkgs = {}

                for k, srv in npm_servers.items():
                    pkg = srv["args"][1] if srv.get("args") else k
                    pkg_base = pkg.split("/")[-1]
                    installed = any(
                        key == pkg or key == pkg_base or key.endswith(f"/{pkg_base}")
                        for key in global_pkgs
                    )
                    if not installed:
                        try:
                            probe = subprocess.run(
                                ["npx", "--no-install", pkg, "--version"],
                                capture_output=True, timeout=8
                            )
                            installed = probe.returncode == 0
                        except Exception:
                            installed = False
                    if not installed:
                        manquants.append(pkg)

        # ── UVX / Python ─────────────────────────────────────────────────────
        if uvx_servers:
            if not shutil.which("uvx") and not shutil.which("uv"):
                for k, srv in uvx_servers.items():
                    pkg = srv["args"][0] if srv.get("args") else k
                    manquants.append(pkg)
                logger.log_error(
                    "uv / uvx est introuvable dans le PATH.\n"
                    "  Installez uv : https://docs.astral.sh/uv/\n"
                    "  curl -LsSf https://astral.sh/uv/install.sh | sh"
                )
            else:
                for k, srv in uvx_servers.items():
                    pkg = srv["args"][0] if srv.get("args") else k
                    # Vérifie via pip show (rapide, sans exécution)
                    pip_name = pkg.replace("-", "_")
                    try:
                        probe = subprocess.run(
                            [sys.executable, "-m", "pip", "show", pip_name],
                            capture_output=True, timeout=8
                        )
                        installed = probe.returncode == 0
                    except Exception:
                        installed = False
                    if not installed:
                        manquants.append(pkg)

        # ── Affichage des erreurs ─────────────────────────────────────────────
        if manquants:
            ok = False
            print(f"\n❌ {len(manquants)} serveur(s) MCP non installé(s) :", file=sys.stderr)
            for pkg in manquants:
                hint = INSTALLATION_INSTRUCTIONS.get(pkg, f"npm install -g {pkg}")
                print(f"\n{border}", file=sys.stderr)
                print(f"  ⚠️  Package manquant : {pkg}", file=sys.stderr)
                print(f"\n  Comment l'installer :", file=sys.stderr)
                for line in hint.splitlines():
                    print(f"    {line}", file=sys.stderr)
            print(f"{border}\n", file=sys.stderr)
            logger.log_error(
                f"{len(manquants)} serveur(s) MCP manquant(s) : {', '.join(manquants)}"
            )

        # ── Variables d'environnement requises ────────────────────────────────
        for nom, srv in selection.items():
            env_var = srv.get("env_var")
            if env_var and not os.environ.get(env_var):
                logger.log_error(
                    f"Variable d'environnement manquante pour le serveur '{nom}' : {env_var}\n"
                    f"  Définissez-la avec : export {env_var}=<votre_token>"
                )
                ok = False

        if ok:
            logger.log_info("Tous les serveurs MCP sont correctement installés.")

        return ok

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
