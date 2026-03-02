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
    dry_run: bool
        Mode simulation.
"""

from abc import abstractmethod
from pathlib import Path
from typing import Optional
from git_ia_assistant.core.definition.ia_assistant import IaAssistant


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
    ):
        super().__init__()
        self.url_mr = url_mr
        self.plateforme = plateforme
        self.numero_mr = numero_mr
        self.out_dir = out_dir
        self.dry_run = dry_run

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
