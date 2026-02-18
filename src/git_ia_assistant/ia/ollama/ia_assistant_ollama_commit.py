#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Classe commit pour l'IA Ollama.
"""

import subprocess
from git_ia_assistant.core.definition.ia_assistant_commit import IaAssistantCommit


class IaAssistantOllamaCommit(IaAssistantCommit):
    """
    Implémentation de la génération de message de commit via Ollama.
    """
    def _envoyer_prompt_ia(self, prompt: str) -> str:
        """
        Envoie le prompt à l'exécutable Ollama et retourne la réponse.

        :param prompt: Le prompt à envoyer.
        :return: La réponse texte de l'IA.
        """
        try:
            # Note: Assurez-vous que le modèle 'commit-message' est bien configuré dans Ollama.
            result = subprocess.run(
                ["ollama", "run", "commit-message"],
                input=prompt.encode(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            if result.returncode != 0:
                return f"Erreur Ollama (stderr): {result.stderr.decode()}"
            return result.stdout.decode().strip()
        except FileNotFoundError:
            return "Erreur: La commande 'ollama' n'a pas été trouvée. Assurez-vous qu'Ollama est installé et dans votre PATH."
        except Exception as e:
            return f"Erreur inattendue lors de l'appel à Ollama: {e}"
