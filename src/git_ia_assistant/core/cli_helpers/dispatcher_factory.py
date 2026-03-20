"""Factory simple pour dispatcher les wrappers CLI vers les modules cibles.

Fournit une API centralisée pour enregistrer des entries et dispatcher en
fonction d'un mode (par ex. 'commit', 'review'). Chaque entrée contient :
- module_path : chemin d'import du module
- remove_flags : flags à retirer de sys.argv avant la délégation

But: remplacer les chaînes hardcodées dans les wrappers par des appels à cette
factory pour faciliter l'ajout de nouveaux modes et centraliser la configuration.
"""
from dataclasses import dataclass
from typing import Dict, Iterable, Optional

from git_ia_assistant.core.cli_helpers.dispatcher_helpers import deleguer_module


@dataclass
class DispatchEntry:
    module_path: str
    remove_flags: Optional[Iterable[str]] = None


class DispatcherFactory:
    def __init__(self):
        self._registry: Dict[str, DispatchEntry] = {}

    def register(self, mode: str, module_path: str, remove_flags: Optional[Iterable[str]] = None) -> None:
        self._registry[mode] = DispatchEntry(module_path=module_path, remove_flags=remove_flags)

    def dispatch(self, mode: str, exit_after: bool = False) -> None:
        if mode not in self._registry:
            raise KeyError(f"Mode inconnu pour dispatcher: {mode}")
        entry = self._registry[mode]
        deleguer_module(entry.module_path, remove_flags=entry.remove_flags, exit_after=exit_after)


# instance globale pré-configurée
factory = DispatcherFactory()
# enregistrement par défaut
from git_ia_assistant.core.cli_mcp_helpers import local_mcp_commit_helpers as commit_mcp_helpers
factory.register("commit_mcp", commit_mcp_helpers.MODULE_PATH, remove_flags=["--mcp"])  # MCP commit
factory.register("commit_local", "git_ia_assistant.core.cli_helpers.local_commit_helpers", remove_flags=None)  # local commit
# Review modes
from git_ia_assistant.core.cli_helpers import local_mr_mcp_review_helpers as review_mcp_helpers

factory.register("review_mcp", review_mcp_helpers.MODULE_PATH, remove_flags=["--mcp"])  # MCP review
factory.register("review_local", "git_ia_assistant.core.cli_helpers.local_mr_review_helpers", remove_flags=None)  # local review
