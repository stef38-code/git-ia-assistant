#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    ia_copilot_mr - Implémentation Copilot pour la revue de MR/PR.

DESCRIPTION
    Classe concrète utilisant GitHub Copilot pour générer des revues de
    Merge Request (GitLab) ou Pull Request (GitHub). Hérite de IaAssistantMr
    et implémente la méthode de génération de revue via l'API Copilot.

FUNCTIONS
    generer_revue_mr(diff_path, resume_path)
        Génère une revue de MR/PR en utilisant Copilot.
"""

from pathlib import Path
from typing import Optional
from git_ia_assistant.core.definition.ia_assistant_mr import IaAssistantMr
from python_commun.ai.copilot import envoyer_prompt_copilot
from python_commun.ai.prompt import charger_prompt, formatter_prompt
from python_commun.logging import logger


class IaCopilotMr(IaAssistantMr):
    """
    Implémentation Copilot pour la revue de Merge Request / Pull Request.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def generer_revue_mr(
        self, diff_path: Path, resume_path: Path
    ) -> Optional[str]:
        """
        Génère une revue de la MR/PR en utilisant GitHub Copilot.

        :param diff_path: Chemin vers le fichier contenant le diff complet.
        :param resume_path: Chemin vers le fichier contenant le résumé de la MR.
        :return: Le texte de la revue générée par Copilot, ou None si erreur.
        """
        try:
            # Charger le contenu des fichiers
            contenu_diff = (
                diff_path.read_text(encoding="utf-8") if diff_path.exists() else ""
            )
            contenu_resume = (
                resume_path.read_text(encoding="utf-8") if resume_path.exists() else ""
            )

            # Charger et formatter le prompt adapté au langage détecté et au modèle
            prompt_template = charger_prompt(
                self._choisir_prompt_mr(), self.dossier_prompts
            )
            
            # Formatter les informations de migration
            migration_detectee = "oui" if self.migration_info.get("detected", False) else "non"
            migration_details = ""
            if self.migration_info.get("detected", False) and self.migration_info.get("migrations"):
                for mig in self.migration_info.get("migrations", []):
                    langage = mig.get("langage", "").capitalize()
                    version_source = mig.get("version_source", "inconnue")
                    version_target = mig.get("version_target", "inconnue")
                    migration_details += f"* Version source {langage} : {version_source}\n"
                    migration_details += f"* Version de destination {langage} : {version_target}\n"
            
            # Formater le langage pour l'expertise (remplacer "/" par "," pour fluidité)
            langage_expertise = self.langage.replace(" / ", ", ")
            
            prompt = formatter_prompt(
                prompt_template,
                url=self.url_mr,
                resume=contenu_resume,
                diff=contenu_diff,
                langage=self.langage,
                langage_expertise=langage_expertise,
                migration_detectee=migration_detectee,
                migration_info=migration_details.strip() if migration_details else "Aucune migration détectée",
                version_cible=self._get_version_cible(),
            )

            # Sauvegarde du prompt généré pour analyse future
            prompt_file = self.out_dir / f"prompt_genere_mr{self.numero_mr}.md"
            try:
                prompt_file.write_text(prompt, encoding="utf-8")
                prompt_saved = True
            except Exception as e:
                logger.log_warning(f"Impossible de sauvegarder le prompt : {e}")
                prompt_saved = False

            if self.dry_run:
                logger.log_console(f"[DRY-RUN] Prompt généré pour Copilot :\n{prompt}")
                return None

            # Affichage de l'emplacement du prompt juste avant l'envoi à l'IA
            if prompt_saved:
                logger.log_info(f"Prompt sauvegardé : {prompt_file}")
            logger.log_info(f"Revue de la MR/PR en cours avec Copilot...")
            result = envoyer_prompt_copilot(prompt)
            return result

        except Exception as e:
            logger.log_error(f"Erreur lors de la génération de la revue Copilot : {e}")
            return None
