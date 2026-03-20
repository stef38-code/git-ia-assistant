"""Helpers pour délégation d'exécution entre wrappers CLI.

Fournit une fonction utilitaire pour importer dynamiquement un module CLI
et appeler sa fonction main() après avoir nettoyé les flags exclus du sys.argv.

Conçu pour être utilisé par les wrappers (commit, review, etc.) afin de centraliser
la logique de délégation et faciliter les tests.
"""
from typing import Iterable, Optional
import importlib
import sys
from python_commun.logging import logger


def deleguer_module(module_str: str, remove_flags: Optional[Iterable[str]] = None, exit_after: bool = False) -> None:
    """Importe dynamiquement module_str et appelle sa fonction main().

    Parameters
    - module_str: chemin d'import du module à déléguer, ex: "git_ia_assistant.cli.commits.commit_mcp_cli"
    - remove_flags: itérable de flags à retirer de sys.argv avant l'import (ex: ["--mcp"]).
    - exit_after: si True, appelle sys.exit(0) après l'exécution (utile pour --help delegation).
    """
    # Nettoyer sys.argv des flags passés
    if remove_flags:
        flags_set = set(remove_flags)
        sys.argv = [a for a in sys.argv if a not in flags_set]

    try:
        module = importlib.import_module(module_str)
    except Exception as e:
        logger.log_error(f"Échec lors de l'import du module '{module_str}': {e}")
        raise

    if not hasattr(module, "main"):
        raise AttributeError(f"Le module '{module_str}' n'expose pas de fonction 'main()'.")

    # Appeler la fonction main du module
    try:
        module.main()
    finally:
        if exit_after:
            sys.exit(0)
