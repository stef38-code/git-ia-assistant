#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    ia_assistant_commit - Classe mère pour la gestion des commits IA.

DESCRIPTION
    Cette classe de base définit l'interface et la logique commune pour la
    génération de messages de commit assistée par IA. Elle gère la détection
    et la préparation des fichiers à commiter, l'obtention du diff,
    et le processus interactif de validation et de push du commit.

FUNCTIONS
    detecter_fichiers()
        Détecte et prépare les fichiers à inclure dans le commit.
    get_diff()
        Retourne le diff des fichiers stagés.
    generer_message_commit()
        Méthode abstraite pour générer le message de commit via une IA.
    valider_commit(message)
        Permet à l'utilisateur de valider, éditer ou annuler le commit,
        puis de le pousser si désiré.

DATA
    fichiers: list
        Liste des chemins des fichiers à analyser.
    repo: git.Repo
        L'objet GitPython représentant le dépôt.
"""

import git
from typing import List
from git_ia_assistant.core.definition.ia_assistant import IaAssistant
import os
from python_commun.logging import logger
from python_commun.system.system import detect_lang_repo


import re


class IaAssistantCommit(IaAssistant):
    """
    Classe mère pour la gestion des commits IA.
    """

    def __init__(self, fichiers: List[str]):
        super().__init__()
        self.fichiers = fichiers
        # Limite de caractères pour le contexte du diff (à ajuster selon le modèle d'IA)
        self.MAX_DIFF_LENGTH = 15000

    def detecter_fichiers(self):
        if not self.fichiers:
            logger.log_info(
                "Aucun fichier spécifié. Préparation de tous les fichiers (git add -A)..."
            )
            self.repo.git.add(A=True)
            fichiers_apres_add = [
                item.a_path
                for item in self.repo.index.diff("HEAD")
                if item.change_type != "D"
            ]
            logger.log_info(
                f"{len(fichiers_apres_add)} fichier(s) détecté(s) (après 'git add -A')"
            )
        else:
            logger.log_info(f"{len(self.fichiers)} fichier(s) spécifié(s) à préparer")
            
            repo_root = self.repo.working_dir
            fichiers_a_ajouter = []
            for f in self.fichiers:
                # Créer un chemin absolu pour une vérification fiable de l'existence
                abs_path = os.path.join(repo_root, f)
                if os.path.exists(abs_path):
                    fichiers_a_ajouter.append(f)
                else:
                    # Avertir si un fichier listé par git n'est pas trouvé, puis l'ignorer
                    logger.log_warn(f"Le fichier '{f}' n'a pas été trouvé sur le disque et sera ignoré.")

            if fichiers_a_ajouter:
                self.repo.git.add(fichiers_a_ajouter)
            else:
                logger.log_info("Aucun fichier existant à ajouter.")

    def get_diff(self) -> str:
        """
        Construit un diff hybride pour l'IA.
        
        :return: Une chaîne de caractères contenant le contexte de diff.
        """
        final_diff_context = ""
        diffs_complets = []
        fichiers_en_resume = []
        current_length = 0

        for fichier in self.fichiers:
            try:
                diff_complet = self.repo.git.diff('--cached', '--', fichier)
                if not diff_complet:
                    continue

                if current_length + len(diff_complet) <= self.MAX_DIFF_LENGTH:
                    diffs_complets.append(diff_complet)
                    current_length += len(diff_complet)
                else:
                    index_fichier_actuel = self.fichiers.index(fichier)
                    fichiers_en_resume = self.fichiers[index_fichier_actuel:]
                    break
            except git.exc.GitCommandError as e:
                logger.log_warn(f"Erreur Git lors de l'obtention du diff pour '{fichier}': {e}")
                continue

        if diffs_complets:
            final_diff_context += "--- Diff complet des modifications ---\n\n"
            final_diff_context += "\n".join(diffs_complets)

        if fichiers_en_resume:
            final_diff_context += "\n\n--- Résumé des fichiers restants (trop volumineux) ---\n\n"
            try:
                resume_stats = self.repo.git.diff('--cached', '--stat', '--', *fichiers_en_resume)
                final_diff_context += resume_stats
            except git.exc.GitCommandError as e:
                logger.log_warn(f"Erreur Git lors de la génération du résumé des fichiers restants: {e}")
                final_diff_context += "Impossible de générer le résumé pour les fichiers restants."

        return final_diff_context

    def _envoyer_prompt_ia(self, prompt: str) -> str:
        """
        Méthode abstraite pour envoyer le prompt à l'IA spécifique.
        Chaque sous-classe doit implémenter cette méthode.

        :param prompt: Le prompt à envoyer à l'IA.
        :return: La réponse brute de l'IA.
        """
        raise NotImplementedError

    def optimiser_commits(self, partiel: bool = False) -> List[dict]:
        """
        Analyse les changements et propose un regroupement en commits logiques.
        
        :param partiel: Si True, permet à un fichier d'être présent dans plusieurs commits.
        :return: Une liste de dictionnaires décrivant les commits suggérés.
        """
        import json
        from python_commun.git.git_core import obtenir_branche_actuelle
        diff = self.get_diff()
        
        try:
            branch_name = obtenir_branche_actuelle(self.repo)
        except Exception:
            branch_name = "unknown"

        try:
            repo_root = self.repo.working_dir or os.getcwd()
            langage = detect_lang_repo(repo_root)
        except Exception:
            langage = "python"

        from python_commun.ai.prompt import charger_prompt
        prompt_template = charger_prompt("optimise_commit_prompt.md", self.dossier_prompts)
        
        prompt = prompt_template.format(
            diff=diff,
            branch_name=branch_name,
            langage=langage,
            partiel=str(partiel)
        )

        raw_response = self._envoyer_prompt_ia(prompt)
        
        # Nettoyage de la réponse pour extraire le JSON
        json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(0))
                return data.get("commits", [])
            except json.JSONDecodeError:
                logger.log_error("Erreur lors du décodage du JSON de regroupement de commits.")
        
        logger.log_warn("Impossible d'extraire des suggestions de commits structurées.")
        return []

    def generer_message_commit(self, instruction_supplementaire: str = "") -> str:
        """
        Génère un message de commit en utilisant une IA.
        Orchestre la création du prompt, l'appel à l'IA et le nettoyage de la réponse.

        :param instruction_supplementaire: Optionnelle, pour affiner le message (ex: "plus court").
        :return: Le message de commit formaté.
        """
        from python_commun.git.git_core import obtenir_branche_actuelle
        diff = self.get_diff()
        
        # Récupération du nom de la branche courante (robuste même en detached HEAD)
        try:
            branch_name = obtenir_branche_actuelle(self.repo)
        except Exception:
            branch_name = "unknown"

        # Détection du langage principal du dépôt
        try:
            repo_root = self.repo.working_dir or os.getcwd()
            langage = detect_lang_repo(repo_root)
        except Exception:
            langage = "python"
        
        from python_commun.ai.prompt import charger_prompt
        prompt_template = charger_prompt("commit_message_prompt.md", self.dossier_prompts)
        if "[Prompt" in prompt_template:
             logger.log_error(f"Fichier de prompt non trouvé dans {self.dossier_prompts}")
             prompt = f"Génère un message de commit au format Conventional Commits pour les changements suivants :\n{diff}"
        else:
            # Injecte les variables attendues par le template (diff, branch_name, langage)
            prompt = prompt_template.format(
                diff=diff,
                branch_name=branch_name,
                langage=langage,
            )
        
        if instruction_supplementaire:
            prompt += f"\n\nIMPORTANT: {instruction_supplementaire}"

        raw_response = self._envoyer_prompt_ia(prompt)

        cleaned_response = re.sub(r'```(git|diff)?', '', raw_response, flags=re.MULTILINE)
        commit_lines = cleaned_response.strip().split('\n')
        start_index = -1
        commit_pattern = re.compile(r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\(.*\))?!?:")
        
        for i, line in enumerate(commit_lines):
            if commit_pattern.match(line.strip()):
                start_index = i
                break

        if start_index != -1:
            final_message = "\n".join(commit_lines[start_index:])
            return final_message.strip()
        else:
            logger.log_warn("Impossible de trouver un titre de commit conventionnel dans la réponse de l'IA.")
            return cleaned_response.strip()

    def valider_commit(self, message: str):
        from python_commun.git.git_core import (
            editer_texte_avec_editeur,
            effectuer_commit_avec_message,
            pousser_vers_distant,
        )

        while True:
            choix = (
                input("Valider le commit ? [y: oui, n: non, e: éditer, a: affiner] [défaut: y] : ")
                .strip()
                .lower()
            )
            if not choix or choix == "y" or choix == "o":
                valider = True
                break
            elif choix == "e":
                message = editer_texte_avec_editeur(message)
                valider = True
                break
            elif choix == "a":
                instruction = input("Instruction pour affiner (ex: 'plus court', 'plus technique') : ").strip()
                if instruction:
                    message = self.generer_message_commit(instruction_supplementaire=instruction)
                    logger.log_console("\nNouveau message généré :\n" + "="*20)
                    logger.log_console(message)
                    logger.log_console("="*20 + "\n")
                continue
            else:
                valider = False
                break
        
        if valider:
            effectuer_commit_avec_message(self.repo, message)
            logger.log_success("Commit effectué avec succès !")

            # Demande de push avec défaut à 'n' et acceptation de 'o' (oui) ou 'y'
            push = input(
                "Pousser le commit sur le dépôt distant ? [y: oui, n: non] [défaut: n] : "
            ).strip().lower()
            if push in ("y", "o"):
                pousser_vers_distant(self.repo)
                logger.log_success("git push effectué !")
            else:
                logger.log_info("Push non effectué. N'oubliez pas de pousser vos changements manuellement.")
        else:
            logger.log_warn("Commit annulé.")

