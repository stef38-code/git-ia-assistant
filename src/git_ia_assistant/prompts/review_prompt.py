#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    review_prompt - Générateur de prompt pour la relecture de code Python MR/PR

DESCRIPTION
    Génère un prompt à partir des informations d'une MR/PR pour l'IA, en utilisant le template markdown python_review_prompt.md.

FUNCTIONS
    generate(title, description, files, diff, author, language, version)
        Génère le prompt formaté pour l'IA.
"""

import os


def generate(
    title: str,
    description: str,
    files: list,
    diff: str,
    author: str,
    language: str,
    version: str,
) -> str:
    """
    Génère le prompt formaté pour l'IA à partir du template markdown et des données MR/PR.

    :param title: Titre de la MR/PR
    :param description: Description de la MR/PR
    :param files: Liste des fichiers modifiés
    :param diff: Diff de la MR/PR
    :param author: Auteur de la MR/PR
    :param language: Langage du projet
    :param version: Version du langage
    :raises FileNotFoundError: Si le template markdown du langage n'existe pas
    :return: Prompt formaté prêt à être envoyé à l'IA
    """
    prompt_filename = f"{language.lower()}_review_prompt.md"
    prompt_path = os.path.join(os.path.dirname(__file__), prompt_filename)
    if not os.path.exists(prompt_path):
        raise FileNotFoundError(
            f"Le template de prompt pour le langage '{language}' est introuvable: {prompt_filename}"
        )
    with open(prompt_path, "r", encoding="utf-8") as f:
        template = f.read()
    prompt = template.format(
        titre=title,
        description=description,
        fichiers="\n".join(files),
        diff=diff,
        auteur=author,
        langage=language,
        version=version,
    )
    return prompt
