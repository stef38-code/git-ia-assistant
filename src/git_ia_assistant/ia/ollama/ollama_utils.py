#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# NAME
# ollama_utils - Module utilitaire pour l'interaction avec Ollama.
#
# RÉFÉRENCE DU MODULE
# Ce module fournit des fonctions pour interagir avec l'API locale d'Ollama.
#
# FUNCTIONS
# appeler_ollama(prompt: str, modele: str = "llama3.1") -> str
#     Envoie une requête à l'API locale d'Ollama et retourne la réponse.
# charger_prompt(nom_prompt: str) -> str
#     Charge le contenu d'un fichier de prompt.
#
# DATA
# OLLAMA_URL = "http://localhost:11434/api/generate"
#

import json
import os
import urllib.request
from python_commun.logging.logger import logger

# Configuration par défaut
OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3.1"


def appeler_ollama(prompt: str, modele: str = DEFAULT_MODEL) -> str:
    """
    Envoie une requête à l'API locale d'Ollama.

    :param prompt: Le prompt à envoyer au modèle.
    :param modele: Le nom du modèle à utiliser.
    :return: La réponse générée par le modèle.
    :raises Exception: En cas d'erreur de communication avec l'API.
    """
    donnees = {"model": modele, "prompt": prompt, "stream": False}

    corps = json.dumps(donnees).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_URL, data=corps, headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req) as reponse:
            resultat = json.loads(reponse.read().decode("utf-8"))
            return resultat.get("response", "")
    except Exception as e:
        logger.log_error(f"Erreur lors de l'appel à Ollama ({modele}) : {e}")
        logger.log_info("Assurez-vous que le serveur Ollama est lancé (ollama-start).")
        raise


def charger_prompt(nom_prompt: str) -> str:
    """
    Charge le contenu d'un fichier de prompt.

    :param nom_prompt: Le nom du fichier de prompt à charger.
    :return: Le contenu du fichier de prompt.
    """
    # Le chemin est relatif à ce fichier (ia_assistant/ollama/ollama_utils.py)
    # On remonte d'un niveau pour arriver à ia_assistant, puis git_ia_assistant.prompts
    chemin_prompt = os.path.join(os.path.dirname(__file__), "..", "prompts", nom_prompt)
    try:
        with open(chemin_prompt, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.die(f"Le fichier de prompt '{chemin_prompt}' est introuvable.")
