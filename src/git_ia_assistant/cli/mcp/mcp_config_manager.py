#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import sys
from typing import Optional, List, Dict
from python_commun.logging import logger
from python_commun.system.system import executer_capture, verifier_commande

from python_commun.ai import sauvegarder_config_mcp

# Constantes pour les paquets MCP réutilisés
PAQUET_FILESYSTEM = "@modelcontextprotocol/server-filesystem"
PAQUET_RIPGREP = "mcp-ripgrep@latest"

# Instructions d'installation pour chaque serveur MCP
INSTRUCTIONS_INSTALLATION = {
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
    PAQUET_FILESYSTEM: (
        f"npm install -g {PAQUET_FILESYSTEM}\n"
        f"  ou via npx : npx -y {PAQUET_FILESYSTEM}"
    ),
    PAQUET_RIPGREP: (
        f"npm install -g {PAQUET_RIPGREP}\n"
        f"  ou via npx : npx -y {PAQUET_RIPGREP}"
    ),
}

SERVEURS_MCP = {
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
        "args": ["-y", PAQUET_FILESYSTEM]
    },
    "search": {
        "command": "npx",
        "args": ["-y", PAQUET_RIPGREP]
    }
}

class McpConfigManager:

    @staticmethod
    def _obtenir_paquets_npm_globaux() -> Dict:
        """
        Récupère la liste des paquets NPM installés globalement.

        :return: Dictionnaire des dépendances globales.
        """
        try:
            resultat = executer_capture(
                ["npm", "list", "-g", "--depth=0", "--json"],
                check=False
            )
            stdout_str = resultat.stdout.decode("utf-8") if resultat.stdout else ""
            return json.loads(stdout_str).get("dependencies", {}) if stdout_str else {}
        except Exception:
            return {}

    @staticmethod
    def _est_paquet_npm_disponible(paquet: str, paquets_globaux: Dict) -> bool:
        """
        Vérifie si un paquet NPM est disponible (installé globalement ou via npx).

        :param paquet: Nom du paquet à vérifier.
        :param paquets_globaux: Dictionnaire des paquets installés globalement.
        :return: True si disponible, False sinon.
        """
        paquet_base = paquet.split("/")[-1]
        
        # 1. Vérification dans les paquets globaux
        trouve_globalement = any(
            cle == paquet or cle == paquet_base or cle.endswith(f"/{paquet_base}")
            for cle in paquets_globaux
        )
        if trouve_globalement:
            return True
            
        # 2. Vérification alternative via npx sans installation
        try:
            test_execution = executer_capture(
                ["npx", "--no-install", paquet, "--version"],
                check=False
            )
            return test_execution.returncode == 0
        except Exception:
            return False

    @staticmethod
    def _verifier_serveurs_npm(serveurs_npm: Dict, manquants: List) -> None:
        """
        Vérifie l'installation des serveurs basés sur Node.js/NPM.

        :param serveurs_npm: Dictionnaire des serveurs NPM à vérifier.
        :param manquants: Liste des paquets manquants à remplir.
        """
        if not serveurs_npm:
            return

        # Vérification de la présence de Node.js et npx
        if not verifier_commande("npx") or not verifier_commande("node"):
            for config in serveurs_npm.values():
                paquet = config["args"][1] if config.get("args") else "inconnu"
                manquants.append(paquet)
            logger.log_error(
                "Node.js / npx est introuvable dans le PATH.\n"
                "  Installez Node.js (≥ 18) : https://nodejs.org"
            )
            return

        paquets_globaux = McpConfigManager._obtenir_paquets_npm_globaux()

        for nom, config in serveurs_npm.items():
            paquet = config["args"][1] if config.get("args") else nom
            if not McpConfigManager._est_paquet_npm_disponible(paquet, paquets_globaux):
                manquants.append(paquet)

    @staticmethod
    def _verifier_serveurs_uvx(serveurs_uvx: Dict, manquants: List) -> None:
        """
        Vérifie l'installation des serveurs basés sur Python/uv.

        :param serveurs_uvx: Dictionnaire des serveurs UVX à vérifier.
        :param manquants: Liste des paquets manquants à remplir.
        """
        if not serveurs_uvx:
            return

        # Vérification de la présence de uv / uvx
        if not verifier_commande("uvx") and not verifier_commande("uv"):
            for config in serveurs_uvx.values():
                paquet = config["args"][0] if config.get("args") else "inconnu"
                manquants.append(paquet)
            logger.log_error(
                "uv / uvx est introuvable dans le PATH.\n"
                "  Installez uv : https://docs.astral.sh/uv/\n"
                "  curl -LsSf https://astral.sh/uv/install.sh | sh"
            )
            return

        for nom, config in serveurs_uvx.items():
            paquet = config["args"][0] if config.get("args") else nom
            # Vérification via pip show (rapide, sans exécution du serveur)
            pip_nom = paquet.replace("-", "_")
            try:
                test_execution = executer_capture(
                    [sys.executable, "-m", "pip", "show", pip_nom],
                    check=False
                )
                est_installe = (test_execution.returncode == 0)
            except Exception:
                est_installe = False
            
            if not est_installe:
                manquants.append(paquet)

    @staticmethod
    def _afficher_erreurs_installation(manquants: List[str], bordure: str) -> None:
        """
        Affiche les instructions d'installation pour les serveurs manquants.

        :param manquants: Liste des paquets manquants.
        :param bordure: Chaîne de caractères utilisée comme séparateur visuel.
        """
        print(f"\n❌ {len(manquants)} serveur(s) MCP non installé(s) :", file=sys.stderr)
        for paquet in manquants:
            conseil = INSTRUCTIONS_INSTALLATION.get(paquet, f"npm install -g {paquet}")
            print(f"\n{bordure}", file=sys.stderr)
            print(f"  ⚠️  Paquet manquant : {paquet}", file=sys.stderr)
            print("\n  Comment l'installer :", file=sys.stderr)
            for ligne in conseil.splitlines():
                print(f"    {ligne}", file=sys.stderr)
        print(f"{bordure}\n", file=sys.stderr)
        logger.log_error(
            f"{len(manquants)} serveur(s) MCP manquant(s) : {', '.join(manquants)}"
        )

    @staticmethod
    def _verifier_variables_environnement(serveurs_selectionnes: Dict) -> bool:
        """
        Vérifie la présence des variables d'environnement requises pour les serveurs sélectionnés.

        :param serveurs_selectionnes: Dictionnaire des serveurs sélectionnés pour la vérification.
        :return: True si toutes les variables sont présentes, False sinon.
        """
        ok = True
        for nom, config in serveurs_selectionnes.items():
            var_env = config.get("env_var")
            if var_env and not os.environ.get(var_env):
                logger.log_error(
                    f"Variable d'environnement manquante pour le serveur '{nom}' : {var_env}\n"
                    f"  Définissez-la avec : export {var_env}=<votre_token>"
                )
                ok = False
        return ok

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
            Liste de clés de ``SERVEURS_MCP`` à vérifier.
            Si ``None``, vérifie tous les serveurs présents dans ``SERVEURS_MCP``.

        Returns
        -------
        bool
            ``True`` si tout est correct, ``False`` si au moins un problème a été détecté.
        """
        bordure = "─" * 60
        serveurs_selectionnes = {
            nom: config for nom, config in SERVEURS_MCP.items() 
            if servers is None or nom in servers
        }

        # Séparation des serveurs selon leur lanceur
        serveurs_npm = {
            nom: conf for nom, conf in serveurs_selectionnes.items() 
            if conf["command"] == "npx"
        }
        serveurs_uvx = {
            nom: conf for nom, conf in serveurs_selectionnes.items() 
            if conf["command"] == "uvx"
        }

        manquants = []

        # ── Vérification des paquets ──────────────────────────────────────────
        McpConfigManager._verifier_serveurs_npm(serveurs_npm, manquants)
        McpConfigManager._verifier_serveurs_uvx(serveurs_uvx, manquants)

        # ── Affichage des erreurs ─────────────────────────────────────────────
        if manquants:
            McpConfigManager._afficher_erreurs_installation(manquants, bordure)

        # ── Vérification de l'environnement ───────────────────────────────────
        env_ok = McpConfigManager._verifier_variables_environnement(serveurs_selectionnes)

        est_valide = (not manquants) and env_ok
        if est_valide:
            logger.log_info("Tous les serveurs MCP sont correctement installés.")

        return est_valide

    @staticmethod
    def generer_config(out_dir, plateforme, langage, token=None, repo_path=None):
        """
        Génère un fichier mcp-config.json adapté au projet et à l'IA choisie.

        :param out_dir: Répertoire où générer le fichier.
        :param plateforme: 'github' ou 'gitlab'.
        :param langage: Langage principal du projet.
        :param token: Token d'accès optionnel.
        :param repo_path: Chemin optionnel vers le dépôt pour filesystem/search.
        :return: Chemin vers le fichier généré ou None.
        """
        config = {"mcpServers": {}}
        langage_minuscule = langage.lower()
        
        # Serveur Git de base
        config["mcpServers"]["git"] = SERVEURS_MCP["git"]
        
        # Serveurs de plateforme
        if plateforme.lower() == "github":
            config["mcpServers"]["github"] = SERVEURS_MCP["github"].copy()
            if token: 
                config["mcpServers"]["github"]["env"] = {"GITHUB_PERSONAL_ACCESS_TOKEN": token}
        elif plateforme.lower() == "gitlab":
            config["mcpServers"]["gitlab"] = SERVEURS_MCP["gitlab"].copy()
            if token: 
                config["mcpServers"]["gitlab"]["env"] = {"GITLAB_PRIVATE_TOKEN": token}
        
        # Outils transverses
        config["mcpServers"]["sequential-thinking"] = SERVEURS_MCP["sequential-thinking"]
        
        # Outils spécifiques au langage
        if "typescript" in langage_minuscule or "angular" in langage_minuscule:
            config["mcpServers"]["typescript"] = SERVEURS_MCP["typescript"]
        if "angular" in langage_minuscule:
            config["mcpServers"]["angular"] = SERVEURS_MCP["angular"]
            
        # SonarQube si token présent
        sonar_token = os.environ.get("SONAR_TOKEN")
        if sonar_token:
            config["mcpServers"]["sonarqube"] = SERVEURS_MCP["sonarqube"].copy()
            config["mcpServers"]["sonarqube"]["env"] = {"SONAR_TOKEN": sonar_token}
            
        # Serveurs de fichiers (si un chemin de dépôt est fourni)
        if repo_path:
            config["mcpServers"]["filesystem"] = {
                "command": "npx",
                "args": ["-y", PAQUET_FILESYSTEM, str(repo_path)]
            }
            config["mcpServers"]["search"] = {
                "command": "npx",
                "args": ["-y", PAQUET_RIPGREP, "--directory", str(repo_path)]
            }
            
        # Écriture du fichier via l'utilitaire commun
        return sauvegarder_config_mcp(config, out_dir)
