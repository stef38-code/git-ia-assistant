"""Helpers pour le module MCP de MR review placé dans core.cli_helpers.

Contient le chemin du module MCP et un petit wrapper utilitaire pour faciliter
la délégation depuis la factory/les wrappers CLI.
"""

MODULE_PATH = "git_ia_assistant.cli.review.mr_review_mcp_cli"


def get_mcp_mr_module_path() -> str:
    """Retourne le chemin d'import du module MCP pour les revues MR/PR."""
    return MODULE_PATH


def deleguer_a_mcp(remove_flags=None, exit_after=False):
    """Délègue l'exécution au module MCP via dispatcher_helpers."""
    from git_ia_assistant.core.cli_helpers.dispatcher_helpers import deleguer_module
    deleguer_module(MODULE_PATH, remove_flags=remove_flags, exit_after=exit_after)
