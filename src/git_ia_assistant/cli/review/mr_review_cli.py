#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wrapper unifié pour la commande `mr_review`.

Délègue vers la version locale (core.cli_helpers.local_mr_review_helpers) ou
vers la version MCP (cli.review.mr_review_mcp_cli) selon la présence du flag
--mcp. La logique d'aide (-h/--help) est redirigée de la même manière.
"""
import os
import sys

# Ajouter chemins pour imports locaux si exécuté directement
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../libs/python_commun/src")))

from git_ia_assistant.core.cli_helpers.dispatcher_factory import factory as dispatcher_factory

HELP_FLAGS = ("-h", "--help")
has_help = any(flag in sys.argv for flag in HELP_FLAGS)
has_mcp = "--mcp" in sys.argv

if has_help:
    if has_mcp:
        dispatcher_factory.dispatch("review_mcp", exit_after=True)
    else:
        dispatcher_factory.dispatch("review_local", exit_after=True)

if has_mcp:
    dispatcher_factory.dispatch("review_mcp")
else:
    dispatcher_factory.dispatch("review_local")
