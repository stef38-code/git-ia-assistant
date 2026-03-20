#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wrapper unifié pour la commande `commit`.

Choisit automatiquement entre le mode local (ancien commit_cli.py) et le mode MCP
(commit_mcp_cli.py). Le choix peut être forcé via l'option --mcp.

Comportement spécial pour l'aide : le flag -h/--help est intercepté par le wrapper
et redirigé vers la cible correspondante (local ou MCP). Ceci permet de conserver
add_help=False dans les sous-modules tout en affichant correctement l'aide.
"""
import os
import sys

# S'assurer que le chemin racine du package est disponible quand on exécute le script directement
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../libs/python_commun/src")))

from git_ia_assistant.core.cli_helpers.dispatcher_factory import factory as dispatcher_factory
from git_ia_assistant.core.cli_mcp_helpers import local_mcp_commit_helpers as mcp_helpers

HELP_FLAGS = ("-h", "--help")
has_help = any(flag in sys.argv for flag in HELP_FLAGS)
has_mcp = "--mcp" in sys.argv

# Si l'utilisateur a demandé l'aide, rediriger explicitement vers la cible appropriée.
if has_help:
    if has_mcp:
        dispatcher_factory.dispatch("commit_mcp", exit_after=True)
    else:
        dispatcher_factory.dispatch("commit_local", exit_after=True)

# Si '--mcp' est présent, déléguer au CLI MCP (commit_mcp_cli)
if has_mcp:
    dispatcher_factory.dispatch("commit_mcp")
else:
    # Mode local : déléguer via la factory
    dispatcher_factory.dispatch("commit_local")
