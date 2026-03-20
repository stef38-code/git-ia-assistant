"""Helpers pour le module MCP de commit.

Contient le chemin du module MCP et un petit wrapper utilitaire pour faciliter
la délégation depuis les wrappers CLI.
"""

MODULE_PATH = "git_ia_assistant.cli.commits.commit_mcp_cli"


def get_mcp_commit_module_path() -> str:
    """Retourne le chemin d'import du module MCP pour les commits."""
    return MODULE_PATH


def deleguer_a_mcp(remove_flags=None, exit_after=False):
    """Wrapper utilitaire qui délègue l'exécution au module MCP via dispatcher_helpers.

    remove_flags : liste de flags à retirer de sys.argv (ex: ['--mcp'])
    exit_after : transmettre à dispatcher_helpers.deleguer_module
    """
    from git_ia_assistant.core.cli_helpers.dispatcher_helpers import deleguer_module
    deleguer_module(MODULE_PATH, remove_flags=remove_flags, exit_after=exit_after)
