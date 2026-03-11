#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    ia_assistant_mr - Classe mère pour la revue de MR/PR avec IA.

DESCRIPTION
    Cette classe de base définit l'interface et la logique commune pour la
    génération de revues de Merge Request (GitLab) ou Pull Request (GitHub)
    assistée par IA. Elle gère le téléchargement du diff, le calcul des
    statistiques et la génération du document de revue.

FUNCTIONS
    generer_revue_mr()
        Méthode abstraite pour générer la revue de MR/PR via une IA.

DATA
    url_mr: str
        URL de la MR/PR à analyser.
    plateforme: str
        Plateforme (gitlab ou github).
    numero_mr: str
        Numéro de la MR/PR.
    out_dir: Path
        Répertoire de sortie pour les fichiers générés.
    langage: str
        Langage principal du projet détecté.
    dry_run: bool
        Mode simulation.
    migration_info: dict
        Informations sur les migrations détectées (detected: bool, migrations: list).
    versions_actuelles: dict
        Versions actuelles des langages/frameworks détectées dans le projet
        (ex: {"angular": "20.1.0", "typescript": "5.4.0"}).
    ia_name: str
        Nom de l'IA utilisée (copilot, gemini, ollama).

FUNCTIONS
    _choisir_prompt_mr()
        Sélectionne le fichier de prompt adapté au langage détecté et à l'IA.
    _get_version_cible()
        Retourne la version majeure cible du langage (migration ou version actuelle).
"""

import os
from abc import abstractmethod
from pathlib import Path
from typing import Optional
from git_ia_assistant.core.definition.ia_assistant import IaAssistant

# Correspondance langage détecté → fichier de prompt spécialisé
_PROMPT_PAR_LANGAGE = {
    "java": "review/mr_review_java_prompt.md",
    "spring": "review/mr_review_java_prompt.md",
    "python": "review/mr_review_python_prompt.md",
    "angular": "review/mr_review_angular_prompt.md",
    "typescript": "review/mr_review_angular_prompt.md",
}
_PROMPT_GENERIQUE = "review/mr_review_prompt.md"


class IaAssistantMr(IaAssistant):
    """
    Classe de base pour la revue de Merge Request / Pull Request avec IA.
    """

    def __init__(
        self,
        url_mr: str,
        plateforme: str,
        numero_mr: str,
        out_dir: Path,
        dry_run: bool = False,
        langage: str = "Unknown",
        migration_info: dict = None,
        versions_actuelles: dict = None,
        ia_name: str = "auto",
    ):
        super().__init__(require_repo=False)
        self.url_mr = url_mr
        self.plateforme = plateforme
        self.numero_mr = numero_mr
        self.out_dir = out_dir
        self.dry_run = dry_run
        self.langage = langage
        self.migration_info = migration_info or {"detected": False, "migrations": []}
        self.versions_actuelles = versions_actuelles or {}
        self.ia_name = ia_name

    def _choisir_prompt_mr(self) -> str:
        """
        Sélectionne le fichier de prompt adapté au langage détecté et à l'IA utilisée.

        Logique de recherche :
        1. Prompt spécifique au langage ET à l'IA (ex: mr_review_angular_gemini_prompt.md)
        2. Prompt spécifique au langage (ex: mr_review_angular_prompt.md)
        3. Prompt générique spécifique à l'IA (ex: mr_review_gemini_prompt.md)
        4. Prompt générique par défaut (mr_review_prompt.md)

        :return: Chemin relatif du fichier de prompt à utiliser.
        """
        langage_lower = self.langage.lower()
        ia_suffix = f"_{self.ia_name}" if self.ia_name != "auto" else ""
        
        # 1. & 2. Recherche par langage
        for mot_cle, chemin_prompt in _PROMPT_PAR_LANGAGE.items():
            if mot_cle in langage_lower:
                # Tenter la version spécifique à l'IA (ex: angular_gemini)
                if ia_suffix:
                    chemin_ia_specifique = chemin_prompt.replace("_prompt.md", f"{ia_suffix}_prompt.md")
                    full_path = os.path.join(self.dossier_prompts, chemin_ia_specifique)
                    if os.path.exists(full_path):
                        return chemin_ia_specifique
                
                # Sinon retourner le prompt langage par défaut
                return chemin_prompt
        
        # 3. Tenter le générique spécifique à l'IA
        if ia_suffix:
            chemin_generique_ia = _PROMPT_GENERIQUE.replace("_prompt.md", f"{ia_suffix}_prompt.md")
            full_path = os.path.join(self.dossier_prompts, chemin_generique_ia)
            if os.path.exists(full_path):
                return chemin_generique_ia
                
        # 4. Retourner le prompt générique par défaut
        return _PROMPT_GENERIQUE

    def _get_version_cible(self) -> str:
        """
        Retourne la version majeure cible du langage/framework principal.

        Priorité :
        1. Version de destination si une migration est détectée dans migration_info.
        2. Version actuelle depuis versions_actuelles (cas sans migration).
        3. Chaîne vide si aucune information de version disponible.

        :return: Version majeure (ex: "20") ou chaîne vide.
        """
        langage_lower = self.langage.lower()

        # 1. Migration détectée : utiliser la version de destination
        if self.migration_info.get("detected", False):
            for mig in self.migration_info.get("migrations", []):
                mig_langage = mig.get("langage", "").lower()
                if mig_langage and mig_langage in langage_lower:
                    version = mig.get("version_target", "")
                    return version.split(".")[0] if version else ""

        # 2. Pas de migration : utiliser la version actuelle du projet
        if self.versions_actuelles:
            for langage, version in self.versions_actuelles.items():
                if langage.lower() in langage_lower:
                    return version.split(".")[0] if version else ""

        return ""

    @abstractmethod
    def generer_revue_mr(
        self, diff_path: Path, resume_path: Path
    ) -> Optional[str]:
        """
        Génère une revue de la MR/PR en analysant le diff et le résumé.

        :param diff_path: Chemin vers le fichier contenant le diff complet.
        :param resume_path: Chemin vers le fichier contenant le résumé de la MR.
        :return: Le texte de la revue générée par l'IA, ou None si erreur.
        """
        pass
