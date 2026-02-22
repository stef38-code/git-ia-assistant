#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    copilot_utils - Utilitaires pour les scripts Copilot.

DESCRIPTION
    Ce module fournit des fonctions utilitaires pour les scripts d'intégration
    avec Copilot. Il facilite le chargement et le formatage des prompts
    utilisés pour interagir avec les modèles Copilot, en s'appuyant sur
    les fonctionnalités du module `python_commun.ai.prompt`.

FUNCTIONS
    charger_prompt(nom_prompt: str) -> str
        Charge le contenu d'un fichier de prompt.
    formatter_prompt(template: str, **kwargs) -> str
        Remplace les variables dans le template par les valeurs fournies.

from python_commun.ai.prompt import charger_prompt, formatter_prompt

__all__ = ["charger_prompt", "formatter_prompt"]
"""

from python_commun.ai.prompt import charger_prompt, formatter_prompt

__all__ = ["charger_prompt", "formatter_prompt"]
