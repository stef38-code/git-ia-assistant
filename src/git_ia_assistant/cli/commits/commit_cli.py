#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wrapper unifié pour la commande `commit`.

Choisit automatiquement entre le mode local (ancien commit_cli.py) et le mode MCP
(commit_mcp_cli.py). Le choix peut être forcé via l'option --mcp.
"""
import os
import sys

# S'assurer que le chemin racine du package est disponible quand on exécute le script directement
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../libs/python_commun/src")))

# Si '--mcp' est présent, déléguer au CLI MCP (commit_mcp_cli)
if "--mcp" in sys.argv:
    # retirer notre flag et déléguer
    sys.argv = [a for a in sys.argv if a != "--mcp"]
    from git_ia_assistant.cli.commits import commit_mcp_cli
    commit_mcp_cli.main()
else:
    # Mode local : déléguer vers les helpers locaux
    from git_ia_assistant.core.cli_helpers.local_commit_helpers import main as local_main
    local_main()
