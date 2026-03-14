#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    ia_assistant_mr_factory - Factory pour instancier la classe de revue MR/PR IA.

DESCRIPTION
    Cette factory est responsable de créer et retourner la bonne instance de
    `IaAssistantMr` (par exemple, `IaCopilotMr`, `IaGeminiMr` ou
    `IaOllamaMr`) en fonction de l'IA choisie. Elle centralise
    la logique de sélection et d'importation dynamique des implémentations
    spécifiques à chaque IA pour la revue de Merge Request / Pull Request.

FUNCTIONS
    get_mr_class(ia: str) -> Type[IaAssistantMr]
        Retourne la classe de revue MR/PR IA appropriée selon l'IA choisie.

DATA
    IA_MODULES: Dict[str, str]
        Dictionnaire mappant les noms des IA aux chemins de leurs modules.
    IA_CLASSES: Dict[str, str]
        Dictionnaire mappant les noms des IA aux noms de leurs classes.
"""

from git_ia_assistant.core.definition.ia_assistant_mr import IaAssistantMr
import importlib
from pathlib import Path


class IaAssistantMrFactory:
    """
    Factory pour instancier la bonne classe de revue MR/PR IA.
    """

    IA_MODULES = {
        "copilot": "git_ia_assistant.ia.copilot.ia_copilot_mr",
        "gemini": "git_ia_assistant.ia.gemini.ia_gemini_mr",
        "ollama": "git_ia_assistant.ia.ollama.ia_ollama_mr",
        "copilot_mcp": "git_ia_assistant.ia.copilot.ia_copilot_mr_mcp",
        "gemini_mcp": "git_ia_assistant.ia.gemini.ia_gemini_mr_mcp",
        "ollama_mcp": "git_ia_assistant.ia.ollama.ia_ollama_mr_mcp",
    }
    IA_CLASSES = {
        "copilot": "IaCopilotMr",
        "gemini": "IaGeminiMr",
        "ollama": "IaOllamaMr",
        "copilot_mcp": "IaCopilotMrMcp",
        "gemini_mcp": "IaGeminiMrMcp",
        "ollama_mcp": "IaOllamaMrMcp",
    }

    @classmethod
    def get_mr_class(cls, ia: str):
        """
        Retourne la classe de revue MR/PR appropriée selon l'IA choisie.

        :param ia: Le nom de l'IA (copilot, gemini, ollama).
        :return: La classe correspondante ou la classe de base si non trouvée.
        """
        module_name = cls.IA_MODULES.get(ia)
        class_name = cls.IA_CLASSES.get(ia)
        if not module_name or not class_name:
            return IaAssistantMr
        module = importlib.import_module(module_name)
        return getattr(module, class_name)

    @classmethod
    def create_mr_instance(
        cls,
        ia: str,
        url_mr: str,
        plateforme: str,
        numero_mr: str,
        out_dir: Path,
        dry_run: bool = False,
        langage: str = "Unknown",
        migration_info: dict = None,
        versions_actuelles: dict = None,
        mcp_config_path: Path = None,
    ) -> IaAssistantMr:
        """
        Instancie la classe de revue MR/PR appropriée.

        :param ia: Le nom de l'IA (copilot, gemini, ollama).
        :param url_mr: URL de la MR/PR.
        :param plateforme: Plateforme (gitlab ou github).
        :param numero_mr: Numéro de la MR/PR.
        :param out_dir: Répertoire de sortie.
        :param dry_run: Mode simulation.
        :param langage: Langage détecté.
        :param migration_info: Infos de migration.
        :param versions_actuelles: Versions actuelles.
        :param mcp_config_path: Chemin vers la config MCP.
        :return: Une instance de IaAssistantMr.
        """
        mr_class = cls.get_mr_class(ia)
        return mr_class(
            url_mr=url_mr,
            plateforme=plateforme,
            numero_mr=numero_mr,
            out_dir=out_dir,
            dry_run=dry_run,
            langage=langage,
            migration_info=migration_info,
            versions_actuelles=versions_actuelles,
            ia_name=ia,
            mcp_config_path=mcp_config_path,
        )
