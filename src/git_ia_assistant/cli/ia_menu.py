"""Compatibility shim for older import path.

Some tools/entrypoints reference `git_ia_assistant.cli.ia_menu`.
The real implementation lives in `git_ia_assistant.cli.menu.ia_menu`.
This shim imports and re-exports `main` to preserve backwards compatibility.
"""

from .menu.ia_menu import main  # re-export for older entrypoints

__all__ = ["main"]

if __name__ == "__main__":
    main()
