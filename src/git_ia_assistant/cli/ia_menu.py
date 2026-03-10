#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    ia_menu - Menu interactif professionnel et dynamique pour git-ia-assistant.

DESCRIPTION
    Interface textuelle riche (TUI) automatisée. Ce menu analyse dynamiquement
    les scripts CLI pour fournir une aide colorée et une saisie intelligente.

THÉMATIQUES DU CODE
    1. Configuration & Initialisation : Chargement YAML et setup des chemins.
    2. Interface Utilisateur (UI) : Double panneau prompt_toolkit avec aide colorée.
    3. Workflow Dynamique : Extraction et saisie des arguments (obligatoires et optionnels).
    4. Exécution : Lancement sécurisé via python_commun.
"""

import os
import sys
from typing import List, Optional, Dict
from pathlib import Path

# Résolution des imports standards (ajusté pour src/git_ia_assistant/cli/)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../libs/python_commun/src")))

try:
    from InquirerPy import inquirer
    from InquirerPy.validator import EmptyInputValidator
    from InquirerPy.base.control import Choice as InquirerChoice
    
    from prompt_toolkit.application import Application
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.layout import Layout, VSplit, Window, HSplit
    from prompt_toolkit.widgets import Frame
    from prompt_toolkit.layout.controls import FormattedTextControl
    from prompt_toolkit.formatted_text import ANSI
except ImportError as e:
    print(f"❌ Erreur: Dépendance manquante ({e}).")
    sys.exit(1)

# Imports de la librairie commune
from python_commun.cli.menu_utils import (
    extraire_docstring,
    extraire_aide_commande,
    extraire_options_obligatoires,
    extraire_toutes_options_flags,
    charger_config_yaml
)
from python_commun.cli.usage import colorier_aide
from python_commun.logging import logger
from python_commun.system.system import executer_commande

# ==============================================================================
# 1. CONFIGURATION
# ==============================================================================

# Chemins relatifs au script dans src/git_ia_assistant/cli/
CLI_DIR = Path(__file__).parent
CONFIG_FILE = CLI_DIR.parent / "config" / "ia_menu.yaml"

COMMAND_MAPPING = charger_config_yaml(str(CONFIG_FILE))

# ==============================================================================
# 2. INTERFACE UTILISATEUR (UI)
# ==============================================================================

class MasterSelector:
    """Sélecteur maître à double panneau avec rafraîchissement automatique."""
    def __init__(self):
        self.mode = "help"
        self.selected_value = None
        self.commands = list(COMMAND_MAPPING.keys())
        self.index = 0

        # Panneau droit : Utilisation de FormattedTextControl pour le support ANSI
        self.details_control = FormattedTextControl(text=ANSI(""))
        self.details_window = Window(content=self.details_control, wrap_lines=True)
        self.frame_right = Frame(self.details_window, title=" Détails ")

        # Panneau gauche : Liste des commandes
        self.kb = KeyBindings()
        self._setup_keybindings()
        self.menu_control = FormattedTextControl(self._get_menu_text)
        self.menu_window = Window(content=self.menu_control, width=35)

        self._update_details()

    def _setup_keybindings(self):
        @self.kb.add("up")
        def _(event):
            self.index = (self.index - 1) % len(self.commands)
            self._update_details()

        @self.kb.add("down")
        def _(event):
            self.index = (self.index + 1) % len(self.commands)
            self._update_details()

        @self.kb.add("h")
        def _(event):
            self.mode = "help"
            self._update_details()

        @self.kb.add("o")
        def _(event):
            self.mode = "options"
            self._update_details()

        @self.kb.add("enter")
        def _(event):
            self.selected_value = self.commands[self.index]
            event.app.exit()

        @self.kb.add("q")
        @self.kb.add("Q")
        @self.kb.add("c-c")
        def _(event):
            self.selected_value = None
            event.app.exit()

    def _get_menu_text(self):
        """Génère le texte enrichi du menu gauche."""
        fragments = []
        for i, cmd in enumerate(self.commands):
            if i == self.index:
                fragments.append(("bg:ansiyellow fg:ansiblack", f" > {cmd} "))
                fragments.append(("", "\n"))
            else:
                fragments.append(("", f"   {cmd} \n"))
        return fragments

    def _update_details(self):
        """Met à jour le panneau droit avec coloration ANSI."""
        cmd = self.commands[self.index]
        script_path = CLI_DIR / COMMAND_MAPPING[cmd]
        
        # Vérification de l'existence du script
        if not script_path.exists():
            self.details_control.text = ANSI(f"\n❌ Fichier introuvable :\n{script_path}")
            return

        doc = extraire_docstring(str(script_path))
        
        if self.mode == "help":
            content = extraire_aide_commande(doc)
            # Forcer la coloration pour l'affichage TUI
            os.environ["FORCE_COLOR"] = "1"
            colored_content = colorier_aide(content)
            title = " Aide "
        else:
            obligatoires = extraire_options_obligatoires(doc)
            optionnels = extraire_toutes_options_flags(doc)
            
            lines = ["\nStructure des paramètres :\n"]
            if obligatoires:
                lines.append("\n[ OBLIGATOIRES ]")
                for o in obligatoires:
                    lines.append(f" - {o['name'].ljust(15)} : {o['desc']}")
            
            if optionnels:
                lines.append("\n< OPTIONNELS >")
                for o in optionnels:
                    lines.append(f" - {o['flag'].ljust(15)} : {o['desc']}")
            
            if not obligatoires and not optionnels:
                lines.append("\nAucun paramètre détecté.")
                
            colored_content = "\n".join(lines)
            title = " Structure "

        self.frame_right.title = f" {title}: {cmd} "
        self.details_control.text = ANSI(colored_content)

    def run(self) -> Optional[str]:
        layout = Layout(VSplit([
            Frame(self.menu_window, title="🤖 Outils"),
            self.frame_right
        ]))
        app = Application(layout=layout, key_bindings=self.kb, full_screen=False)
        app.run()
        return self.selected_value

# ==============================================================================
# 3. WORKFLOW D'EXÉCUTION
# ==============================================================================

def gerer_workflow_dynamique(cmd_name: str) -> List[str]:
    """Extrait et demande les arguments nécessaires via InquirerPy."""
    script_path = CLI_DIR / COMMAND_MAPPING[cmd_name]
    doc = extraire_docstring(str(script_path))
    
    args = []
    
    # 1. Saisie des arguments OBLIGATOIRES
    obligatoires = extraire_options_obligatoires(doc)
    if obligatoires:
        print(f"\n⚙️  Configuration requise pour {cmd_name} :")
        for opt in obligatoires:
            val = inquirer.text(
                message=f"   {opt['desc']} :",
                validate=EmptyInputValidator("Ce champ est requis.")
            ).execute()
            if val is None: return [] # Annulation
            
            if opt['name'].startswith('-'):
                args.extend([opt['name'], val])
            else:
                args.append(val)

    # 2. Saisie des options OPTIONNELLES
    optionnels = extraire_toutes_options_flags(doc)
    if optionnels:
        choices = [InquirerChoice(o['flag'], name=f"{o['flag']} ({o['desc']})") for o in optionnels]
        selected_options = inquirer.checkbox(
            message="🛠️  Options additionnelles [Espace pour cocher] :",
            choices=choices,
            instruction="(Enter pour valider)"
        ).execute()
        if selected_options:
            args.extend(selected_options)

    return args

# ==============================================================================
# 4. MAIN
# ==============================================================================

def main():
    print("\n" + "═"*75)
    print(" 🤖 GIT IA ASSISTANT - MENU INTERACTIF")
    print(" [↑/↓]: Navigation  [h]: Aide  [o]: Options  [Enter]: Lancer  [q]: Quitter")
    print("═"*75 + "\n")

    selected_cmd = MasterSelector().run()
    if not selected_cmd:
        print("\n👋 Au revoir !")
        return

    args = gerer_workflow_dynamique(selected_cmd)
    
    full_cmd = [selected_cmd] + args
    logger.log_info(f"Lancement de : {' '.join(full_cmd)}")
    print("")
    
    try:
        executer_commande(full_cmd)
    except Exception as e:
        logger.log_error(f"Échec de l'exécution : {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interruption utilisateur.")
        sys.exit(0)
