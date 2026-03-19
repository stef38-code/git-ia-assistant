#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    ia_menu - Menu interactif professionnel et dynamique pour git-ia-assistant.

DESCRIPTION
    Interface textuelle riche (TUI) automatisée. Ce menu analyse dynamiquement
    les scripts CLI pour fournir une aide colorée et une saisie intelligente.
"""

import os
import sys
from pathlib import Path
from typing import List, Optional

# Résolution des imports standards (ajusté pour src/git_ia_assistant/cli/)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../libs/python_commun/src")))

try:
    from InquirerPy import inquirer
    from InquirerPy.validator import EmptyInputValidator
    from InquirerPy.base.control import Choice as InquirerChoice

    from prompt_toolkit.application import Application
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.layout import Layout, VSplit, Window
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
from python_commun.git_ia_shared.menu_utils import trv, srcp, get_help_text

# ==============================================================================
# 1. CONFIGURATION
# ==============================================================================

# Chemins relatifs au script dans src/git_ia_assistant/cli/
CLI = Path(__file__).parent
CFG = CLI.parent.parent / "config" / "ia_menu.yaml"
CMDM = charger_config_yaml(str(CFG))


# ==============================================================================
# 2. INTERFACE UTILISATEUR (UI)
# ==============================================================================

class Menu:
    """Sélecteur TUI à deux panneaux, filtrage et affichage d'aide."""

    def __init__(self):
        self.mod = "help"       # mode d'affichage: 'help' ou 'options'
        self.sel = None          # valeur sélectionnée

        # liste des commandes
        self.allc = list(CMDM.keys())
        self.cmds = self.allc.copy()
        self.idx = 0
        self.filt = ""

        # panneau droit
        self.detc = FormattedTextControl(text=ANSI(""))
        self.detw = Window(content=self.detc, wrap_lines=True)
        self.fr = Frame(self.detw, title=" Détails ")

        # panneau gauche
        self.kb = KeyBindings()
        self._kb()
        self.mctl = FormattedTextControl(self._txt)
        self.mwin = Window(content=self.mctl, width=40)

        self._maj()

    def _fil(self):
        """Applique le filtre self.filt sur la liste self.allc -> self.cmds."""
        if not self.filt:
            self.cmds = self.allc.copy()
        else:
            ft = self.filt.lower()
            self.cmds = [cmd for cmd in self.allc if ft in cmd.lower()]

        if not self.cmds:
            self.idx = 0
        else:
            self.idx = max(0, min(self.idx, len(self.cmds) - 1))

    def _kb(self):
        @self.kb.add("up")
        def _(event):
            if not self.cmds:
                return
            self.idx = (self.idx - 1) % len(self.cmds)
            self._maj()

        @self.kb.add("down")
        def _(event):
            if not self.cmds:
                return
            self.idx = (self.idx + 1) % len(self.cmds)
            self._maj()

        @self.kb.add("f1")
        def _(event):
            self.mod = "help"
            self._maj()

        @self.kb.add("f2")
        def _(event):
            self.mod = "options"
            self._maj()

        @self.kb.add("enter")
        def _(event):
            if not self.cmds:
                return
            self.sel = self.cmds[self.idx]
            event.app.exit()

        @self.kb.add("f10")
        @self.kb.add("c-c")
        def _(event):
            self.sel = None
            event.app.exit()

        @self.kb.add("backspace")
        def _(event):
            if self.filt:
                self.filt = self.filt[:-1]
                self._fil()
                self._maj()

        @self.kb.add("escape")
        def _(event):
            if self.filt:
                self.filt = ""
                self._fil()
                self._maj()

        @self.kb.add("<any>")
        def _(event):
            try:
                key = event.key_sequence[0].key
            except Exception:
                return
            if isinstance(key, str) and len(key) == 1 and key.isprintable():
                self.filt += key
                self._fil()
                self._maj()

    def _txt(self):
        """Texte affiché dans le panneau gauche (liste + filtre)."""
        frags = []
        if self.filt:
            frags.append(("fg:ansiblue", f" Filtre: {self.filt} \n\n"))
        else:
            frags.append(("fg:ansigray italic", " Tapez pour filtrer, Esc pour effacer. \n\n"))

        if not self.cmds:
            frags.append(("fg:ansired", "   Aucun résultat pour ce filtre\n"))
            return frags

        for idx_cmd, cmd_name in enumerate(self.cmds):
            if idx_cmd == self.idx:
                frags.append(("bg:ansiyellow fg:ansiblack", f" > {cmd_name} "))
                frags.append(("", "\n"))
            else:
                frags.append(("", f"   {cmd_name} \n"))
        return frags

    def _maj(self):
        """Met à jour le panneau droit (doc / help / structure des options)."""
        if not self.cmds:
            self.fr.title = " Détails "
            self.detc.text = ANSI("\n🔎 Aucun élément correspondant au filtre.\n")
            return

        cmd = self.cmds[self.idx]
        spth = trv(cmd, mapping=CMDM, base=CLI)

        if not spth.exists():
            self.detc.text = ANSI(f"\n❌ Fichier introuvable :\n{spth}")
            return

        srcd = srcp(spth, base=CLI)

        doc = extraire_docstring(str(srcd))
        if not doc or not doc.strip():
            htxt = get_help_text(spth)
            if htxt.strip():
                os.environ["FORCE_COLOR"] = "1"
                try:
                    colored = colorier_aide(htxt)
                except Exception:
                    colored = htxt
                self.fr.title = f" Aide: {cmd} "
                self.detc.text = ANSI(colored)
                return

            self.detc.text = ANSI(f"\nℹ️  Exécutable trouvé : {spth}\nImpossible d'extraire la docstring ou d'obtenir '--help'.")
            return

        if self.mod == "help":
            content = extraire_aide_commande(doc)
            os.environ["FORCE_COLOR"] = "1"
            colored_content = colorier_aide(content)
            title = " Aide "
        else:
            obli = extraire_options_obligatoires(doc)
            optl = extraire_toutes_options_flags(doc)

            lines = ["\nStructure des paramètres :\n"]
            if obli:
                lines.append("\n[ OBLIGATOIRES ]")
                for opt in obli:
                    lines.append(f" - {opt['name'].ljust(15)} : {opt['desc']}")

            if optl:
                lines.append("\n< OPTIONNELS >")
                for opt in optl:
                    lines.append(f" - {opt['flag'].ljust(15)} : {opt['desc']}")

            if not obli and not optl:
                lines.append("\nAucun paramètre détecté.")

            colored_content = "\n".join(lines)
            title = " Structure "

        self.fr.title = f" {title}: {cmd} "
        self.detc.text = ANSI(colored_content)

    def run(self) -> Optional[str]:
        layout = Layout(VSplit([
            Frame(self.mwin, title="🤖 Outils"),
            self.fr
        ]))
        app = Application(layout=layout, key_bindings=self.kb, full_screen=False)
        app.run()
        return self.sel


# ==============================================================================
# 3. WORKFLOW D'EXÉCUTION
# ==============================================================================

def gerer_workflow_dynamique(cmd: str) -> List[str]:
    """Extrait et demande les arguments nécessaires via InquirerPy."""
    spth = trv(cmd, mapping=CMDM, base=CLI)

    doc = ""
    if spth.exists():
        if spth.suffix == ".py":
            try:
                doc = extraire_docstring(str(spth))
            except Exception:
                doc = ""
        else:
            src = srcp(spth, base=CLI)
            if src and src.exists():
                try:
                    doc = extraire_docstring(str(src))
                except Exception:
                    doc = ""

    if not doc and spth.exists():
        doc = get_help_text(spth)

    args: List[str] = []

    # 1. OBLIGATOIRES
    obli = extraire_options_obligatoires(doc)
    if obli:
        print(f"\n⚙️  Configuration requise pour {cmd} :")
        for opt in obli:
            val = inquirer.text(
                message=f"   {opt['desc']} :",
                validate=EmptyInputValidator("Ce champ est requis.")
            ).execute()
            if val is None:
                return []
            if opt['name'].startswith('-'):
                args.extend([opt['name'], val])
            else:
                args.append(val)

    # 2. OPTIONNELS
    optl = extraire_toutes_options_flags(doc)
    if optl:
        choices = [InquirerChoice(opt['flag'], name=f"{opt['flag']} ({opt['desc']})") for opt in optl]
        sops = inquirer.checkbox(
            message="🛠️  Options additionnelles [Espace pour cocher] :",
            choices=choices,
            instruction="(Enter pour valider)"
        ).execute()
        if sops:
            args.extend(sops)

    return args


# ==============================================================================
# 4. MAIN
# ==============================================================================

def main():
    print("\n" + "═"*75)
    print(" 🤖 GIT IA ASSISTANT - MENU INTERACTIF")
    print(" [↑/↓]: Navigation  [F1]: Aide  [F2]: Options  [Enter]: Lancer  [F10]: Quitter")
    print("═"*75 + "\n")

    selc = Menu().run()
    if not selc:
        print("\n👋 Au revoir !")
        return

    args = gerer_workflow_dynamique(selc)

    fcmd = [selc] + args
    logger.log_info(f"Lancement de : {' '.join(fcmd)}")
    print("")

    try:
        executer_commande(fcmd)
    except Exception as e:
        logger.log_error(f"Échec de l'exécution : {e}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interruption utilisateur.")
        sys.exit(0)
