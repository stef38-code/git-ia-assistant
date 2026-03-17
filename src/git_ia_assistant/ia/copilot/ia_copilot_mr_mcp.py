#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    ia_copilot_mr_mcp - Implémentation Copilot Agentique avec MCP.

DESCRIPTION
    Version MCP de l'assistant Copilot pour la revue de MR/PR.
    Utilise le flag --additional-mcp-config pour donner accès aux outils à Copilot.
"""

from pathlib import Path
from typing import Optional
from git_ia_assistant.core.definition.ia_assistant_mr import IaAssistantMr
from python_commun.ai.copilot import envoyer_prompt_copilot
from python_commun.ai.prompt import charger_prompt, formatter_prompt
from python_commun.logging import logger


class IaCopilotMrMcp(IaAssistantMr):
    """
    Implémentation Copilot Agentique pour la revue de Merge Request / Pull Request.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def generer_revue_mr(
        self, diff_path: Optional[Path] = None, resume_path: Optional[Path] = None
    ) -> Optional[str]:
        """
        Génère une revue de la MR/PR en utilisant GitHub Copilot avec MCP.
        """
        try:
            # Charger le prompt MCP (léger)
            # Construire le nom de fichier du prompt MCP : review/mr_review_<langage>_mcp_prompt.md
            base = self._choisir_prompt_mr()
            if base.endswith("_prompt.md") or base.startswith("review/"):
                prompt_name = base.replace("_prompt.md", "_mcp_prompt.md") if base.endswith("_prompt.md") else base + "_mcp_prompt.md"
            else:
                prompt_name = f"review/{base}_mcp_prompt.md"
            prompt_template = charger_prompt(prompt_name, self.dossier_prompts)
            
            # Formater le prompt
            # Tenter de charger un résumé et la liste des fichiers si disponibles
            resume_text, files_text = self.charger_resume_et_liste()

            prompt = formatter_prompt(
                prompt_template,
                url=self.url_mr,
                resume=resume_text or "Analyse agentique en cours...",
                liste_fichiers=files_text or "Consultable via outils git",
                langage=self.langage,
                migration_detectee=("oui" if self.migration_info.get("detected", False) else "non"),
                migration_info="\n".join([f"* {m}" for m in self.migration_info.get("migrations", [])]) if self.migration_info.get("migrations") else "Aucune migration détectée",
                numero_mr=self.numero_mr,
                version_cible=self._get_version_cible(),
            )

            # Sauvegarde du prompt MCP pour debug
            prompt_file_mcp = self.out_dir / f"prompt_mcp_mr{self.numero_mr}.md"
            try:
                prompt_file_mcp.write_text(prompt, encoding="utf-8")
                prompt_saved = True
            except Exception as e:
                logger.log_warning(f"Impossible de sauvegarder le prompt MCP : {e}")
                prompt_saved = False

            if self.dry_run:
                logger.log_console(f"[DRY-RUN] Prompt Agent MCP pour Copilot :\n{prompt}")
                return None

            if prompt_saved:
                logger.log_info(f"Prompt MCP sauvegardé : {prompt_file_mcp}")

            logger.log_info(f"🤖 Revue Agentique en cours avec Copilot (MCP)...")
            
            # On passe explicitement le mcp_config_path à la fonction d'envoi
            result = envoyer_prompt_copilot(prompt, mcp_config_path=self.mcp_config_path)
            return result

        except Exception as e:
            logger.log_error(f"Erreur lors de la génération de la revue Copilot MCP : {e}")
            return None

    def _choisir_prompt_mr(self) -> str:
        if "angular" in self.langage.lower(): return "mr_review_angular"
        if "python" in self.langage.lower(): return "mr_review_python"
        if "java" in self.langage.lower(): return "mr_review_java"
        return "mr_review"
