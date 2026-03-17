#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pathlib import Path
from typing import Optional
from google import genai
from git_ia_assistant.core.definition.ia_assistant_mr import IaAssistantMr
from python_commun.ai.mcp_client_manager import McpClientManager
from python_commun.ai.prompt import charger_prompt, formatter_prompt
from python_commun.logging import logger

class IaGeminiMrMcp(IaAssistantMr):
    """
    Implémentation Agentique de Gemini utilisant les serveurs MCP.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mcp_manager = None

    def generer_revue_mr(self, diff_path: Optional[Path] = None, resume_path: Optional[Path] = None) -> Optional[str]:
        """
        Génère une revue de la MR/PR en utilisant Google Gemini en mode Agent MCP.
        """
        if not self.mcp_config_path:
            logger.die("Configuration MCP manquante pour le mode Agent Gemini.")

        # Démarrage des serveurs MCP (si non déjà démarrés dans le CLI)
        if not getattr(self, "mcp_manager", None):
            self.mcp_manager = McpClientManager(self.mcp_config_path)
            self.mcp_manager.demarrer_serveurs()
        else:
            logger.log_info("Réutilisation du McpClientManager déjà démarré.")

        try:
            # 1. Préparation du prompt MCP
            # On utilise le prompt spécifique au langage si possible
            nom_base_prompt = self._choisir_prompt_mr()
            # Construire le nom du fichier prompt MCP attendu
            if nom_base_prompt.endswith("_prompt.md") or nom_base_prompt.startswith("review/"):
                prompt_name = nom_base_prompt.replace("_prompt.md", "_mcp_prompt.md") if nom_base_prompt.endswith("_prompt.md") else nom_base_prompt + "_mcp_prompt.md"
            else:
                prompt_name = f"review/{nom_base_prompt}_mcp_prompt.md"
            prompt_template = charger_prompt(prompt_name, self.dossier_prompts)
            
            # En mode Agent, on ne passe pas le diff complet pour économiser les tokens
            resume_text, files_text = self.charger_resume_et_liste()

            prompt = formatter_prompt(
                prompt_template,
                url=self.url_mr,
                resume=resume_text or "Analyse agentique en cours via outils MCP...",
                liste_fichiers=files_text or "Utilise l'outil git.git_diff pour identifier les changements.",
                langage=self.langage,
                migration_detectee=("oui" if self.migration_info.get("detected", False) else "non"),
                migration_info="L'IA doit explorer le code pour détecter les changements de version.",
                numero_mr=self.numero_mr,
                version_cible=self._get_version_cible()
            )

            # Sauvegarde du prompt MCP pour debug
            prompt_file_mcp = self.out_dir / f"prompt_mcp_mr{self.numero_mr}.md"
            try:
                prompt_file_mcp.write_text(prompt, encoding="utf-8")
                prompt_saved = True
            except Exception as e:
                logger.log_warning(f"Impossible de sauvegarder le prompt MCP : {e}")
                prompt_saved = False

            # 2. Configuration du client Gemini
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                logger.die("La variable d'environnement GEMINI_API_KEY n'est pas configurée.")
                
            client = genai.Client(api_key=api_key, http_options={"api_version": "v1"})

            # 3. Exécution de l'Agent
            logger.log_info("🤖 Gemini (Agent MCP) analyse le dépôt...")

            if prompt_saved:
                logger.log_info(f"Prompt MCP sauvegardé : {prompt_file_mcp}")

            # Note: Pour une boucle de tool-calling complète, il faudrait itérer ici.
            # Pour l'instant, nous envoyons le prompt d'investigation.
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            
            return response.text.strip() if hasattr(response, "text") else str(response).strip()

        except Exception as e:
            logger.log_error(f"Erreur lors de la génération de la revue Gemini MCP : {e}")
            return None
        finally:
            if self.mcp_manager:
                try:
                    self.mcp_manager.arreter_serveurs()
                except Exception:
                    pass

    def _choisir_prompt_mr(self) -> str:
        """Choisit le nom du prompt en fonction du langage détecté."""
        lang = self.langage.lower()
        if "angular" in lang:
            return "mr_review_angular"
        elif "python" in lang:
            return "mr_review_python"
        elif "java" in lang:
            return "mr_review_java"
        return "mr_review"
