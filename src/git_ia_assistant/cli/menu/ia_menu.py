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
import shutil
import re
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
from python_commun.system.system import executer_commande, executer_capture

# ==============================================================================
# 1. CONFIGURATION
# ==============================================================================

# Chemins relatifs au script dans src/git_ia_assistant/cli/
CLI_DIR = Path(__file__).parent
# CONFIG_FILE previously pointed to CLI_DIR.parent / "config" which resolves to
# src/git_ia_assistant/cli/config — the actual config lives in
# src/git_ia_assistant/config, so move up one directory.
CONFIG_FILE = CLI_DIR.parent.parent / "config" / "ia_menu.yaml"

COMMAND_MAPPING = charger_config_yaml(str(CONFIG_FILE))


def resolve_command_path(cmd_name: str) -> Path:
    """Résout le chemin d'exécution d'une commande en priorité vers l'exécutable installé.

    Ordre de résolution :
      1) ~/.local/bin/<cmd>
      2) chemin trouvé par `which` (PATH)
      3) fallback : chemin source dans le dépôt (COMMAND_MAPPING)
    Retourne un Path (peut ne pas exister).
    """
    # 1) ~/.local/bin
    local_bin = Path.home() / ".local" / "bin" / cmd_name
    if local_bin.exists() and os.access(str(local_bin), os.X_OK):
        return local_bin

    # 2) which (PATH)
    which_path = shutil.which(cmd_name)
    if which_path:
        return Path(which_path)

    # 3) fallback vers le fichier source référencé dans COMMAND_MAPPING
    mapped = CLI_DIR / COMMAND_MAPPING.get(cmd_name, "")
    return mapped


# ==============================================================================
# 2. INTERFACE UTILISATEUR (UI)
# ==============================================================================

class MasterSelector:
    """Sélecteur maître à double panneau avec rafraîchissement automatique.

    Ajout : saisie filtrée. L'utilisateur peut taper pour filtrer la liste des
    commandes. Backspace supprime, Escape vide le filtre. La navigation par
    flèches fonctionne toujours sur la liste filtrée.
    """
    def __init__(self):
        self.mode = "help"
        self.selected_value = None
        # garder la liste complète et une vue filtrée
        self.all_commands = list(COMMAND_MAPPING.keys())
        self.commands = self.all_commands.copy()
        self.index = 0
        self.filter_text = ""

        # Panneau droit : Utilisation de FormattedTextControl pour le support ANSI
        self.details_control = FormattedTextControl(text=ANSI(""))
        self.details_window = Window(content=self.details_control, wrap_lines=True)
        self.frame_right = Frame(self.details_window, title=" Détails ")

        # Panneau gauche : Liste des commandes
        self.kb = KeyBindings()
        self._setup_keybindings()
        self.menu_control = FormattedTextControl(self._get_menu_text)
        self.menu_window = Window(content=self.menu_control, width=40)

        self._update_details()

    def _apply_filter(self):
        if not self.filter_text:
            self.commands = self.all_commands.copy()
        else:
            ft = self.filter_text.lower()
            self.commands = [c for c in self.all_commands if ft in c.lower()]
        # ajuster l'index
        if not self.commands:
            self.index = 0
        else:
            self.index = max(0, min(self.index, len(self.commands) - 1))

    def _setup_keybindings(self):
        @self.kb.add("up")
        def _(event):
            if not self.commands:
                return
            self.index = (self.index - 1) % len(self.commands)
            self._update_details()

        @self.kb.add("down")
        def _(event):
            if not self.commands:
                return
            self.index = (self.index + 1) % len(self.commands)
            self._update_details()

        @self.kb.add("f1")
        def _(event):
            self.mode = "help"
            self._update_details()

        @self.kb.add("f2")
        def _(event):
            self.mode = "options"
            self._update_details()

        @self.kb.add("enter")
        def _(event):
            if not self.commands:
                # rien à sélectionner
                return
            self.selected_value = self.commands[self.index]
            event.app.exit()

        @self.kb.add("f10")
        @self.kb.add("c-c")
        def _(event):
            self.selected_value = None
            event.app.exit()

        # Backspace pour enlever un caractère du filtre
        @self.kb.add("backspace")
        def _(event):
            if self.filter_text:
                self.filter_text = self.filter_text[:-1]
                self._apply_filter()
                self._update_details()

        # Escape pour vider le filtre
        @self.kb.add("escape")
        def _(event):
            if self.filter_text:
                self.filter_text = ""
                self._apply_filter()
                self._update_details()

        # Capturer les caractères imprimables pour construire le filtre
        @self.kb.add("<any>")
        def _(event):
            try:
                key = event.key_sequence[0].key
            except Exception:
                return
            # Accepter uniquement les caractères imprimables simples
            if isinstance(key, str) and len(key) == 1 and key.isprintable():
                self.filter_text += key
                self._apply_filter()
                self._update_details()
            # Permettre TAB ou autres touches de passer

    def _get_menu_text(self):
        """Génère le texte enrichi du menu gauche, incluant la ligne de filtre."""
        fragments = []
        # Ligne de filtre
        if self.filter_text:
            fragments.append(("fg:ansiblue", f" Filter: {self.filter_text} \n\n"))
        else:
            fragments.append(("fg:ansigray italic", " Tapez pour filtrer, Esc pour effacer. \n\n"))

        if not self.commands:
            fragments.append(("fg:ansired", "   Aucun résultat pour ce filtre\n"))
            return fragments

        for i, cmd in enumerate(self.commands):
            if i == self.index:
                fragments.append(("bg:ansiyellow fg:ansiblack", f" > {cmd} "))
                fragments.append(("", "\n"))
            else:
                fragments.append(("", f"   {cmd} \n"))
        return fragments

    def _update_details(self):
        """Met à jour le panneau droit avec coloration ANSI."""
        if not self.commands:
            # afficher message informatif
            self.frame_right.title = " Détails "
            self.details_control.text = ANSI("\n🔎 Aucun élément correspondant au filtre.\n")
            return

        cmd = self.commands[self.index]
        script_path = resolve_command_path(cmd)

        # Vérification de l'existence du script/exécutable
        if not script_path.exists():
            self.details_control.text = ANSI(f"\n❌ Fichier introuvable :\n{script_path}")
            return

        # Si le chemin résolu est un script Python, extraire la docstring directement.
        source_for_doc = script_path
        if script_path.suffix != ".py":
            # Essayer d'extraire la cible Python d'un wrapper bash (ex: scripts créés par l'install)
            try:
                content = script_path.read_text()
                m = re.search(r'python3?\s+\"([^\"]+\.py)\"', content)
                if m:
                    candidate_str = m.group(1)
                    # Remplacer les variables $INSTALL_DIR ou ${INSTALL_DIR} par le chemin d'installation par défaut
                    install_dir_guess = str(Path.home() / '.local' / 'share' / 'git-ia-assistant')
                    candidate_str = candidate_str.replace('$INSTALL_DIR', install_dir_guess).replace('${INSTALL_DIR}', install_dir_guess)
                    candidate = Path(candidate_str)
                    if not candidate.is_absolute():
                        # tenter une résolution relative au dépôt
                        candidate = (CLI_DIR / candidate).resolve()
                    # Si le chemin n'existe pas (wrapper pointant vers INSTALL_DIR), essayer la copie dans le dépôt (recherche de '/src/')
                    if not candidate.exists():
                        repo_root = CLI_DIR
                        # remonter jusqu'à la racine du dépôt : chercher 'src' dans parents
                        for _ in range(6):
                            repo_root = repo_root.parent
                        # essayer d'extraire le suffixe 'src/...'
                        s = candidate_str
                        idx = s.find('/src/')
                        if idx == -1:
                            idx = s.find('src/')
                        if idx != -1:
                            suffix = s[idx:]
                            candidate_alt = (repo_root / suffix).resolve()
                            if candidate_alt.exists():
                                candidate = candidate_alt
                    if candidate.exists():
                        source_for_doc = candidate
            except Exception:
                # Fallback: on utilisera le binaire/exécutable pour informer l'utilisateur
                source_for_doc = script_path

        # Extraire la docstring si possible
        doc = extraire_docstring(str(source_for_doc))
        if not doc or not doc.strip():
            # Tentative de fallback : exécuter l'exécutable avec --help et capturer la sortie
            try:
                proc = executer_capture([str(script_path), "--help"], check=False)
                # Prefer stdout, fallback to stderr if stdout empty
                if proc.stdout:
                    help_text = proc.stdout.decode() if isinstance(proc.stdout, (bytes, bytearray)) else proc.stdout
                else:
                    help_text = proc.stderr.decode() if proc.stderr else ""
            except Exception:
                help_text = ""

            if help_text.strip():
                # Afficher la sortie --help (colorisée si possible)
                os.environ["FORCE_COLOR"] = "1"
                try:
                    colored = colorier_aide(help_text)
                except Exception:
                    colored = help_text
                self.frame_right.title = f" Aide: {cmd} "
                self.details_control.text = ANSI(colored)
                return

            # Si tout échoue, informer l'utilisateur
            self.details_control.text = ANSI(
                f"\nℹ️  Exécutable trouvé : {script_path}\nImpossible d'extraire la docstring ou d'obtenir '--help'." 
            )
            return
        
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
    script_path = resolve_command_path(cmd_name)

    doc = ""
    if script_path.exists():
        if script_path.suffix == ".py":
            try:
                doc = extraire_docstring(str(script_path))
            except Exception:
                doc = ""
        else:
            # tenter d'extraire la cible Python d'un wrapper
            try:
                content = script_path.read_text()
                m = re.search(r'python3?\s+\"([^\"]+\.py)\"', content)
                if m:
                    candidate_str = m.group(1)
                    install_dir_guess = str(Path.home() / '.local' / 'share' / 'git-ia-assistant')
                    candidate_str = candidate_str.replace('$INSTALL_DIR', install_dir_guess).replace('${INSTALL_DIR}', install_dir_guess)
                    candidate = Path(candidate_str)
                    if not candidate.is_absolute():
                        candidate = (CLI_DIR / candidate).resolve()
                    if not candidate.exists():
                        repo_root = CLI_DIR
                        for _ in range(6):
                            repo_root = repo_root.parent
                        s = candidate_str
                        idx = s.find('/src/')
                        if idx == -1:
                            idx = s.find('src/')
                        if idx != -1:
                            suffix = s[idx:]
                            candidate_alt = (repo_root / suffix).resolve()
                            if candidate_alt.exists():
                                candidate = candidate_alt
                    if candidate.exists():
                        doc = extraire_docstring(str(candidate))
            except Exception:
                # fallback: on pourra exécuter le binaire pour obtenir l'aide si nécessaire
                doc = ""

    # Si docstring vide, tenter de récupérer l'aide via --help
    if not doc and script_path.exists():
        try:
            proc = executer_capture([str(script_path), "--help"], check=False)
            if proc.stdout:
                help_text = proc.stdout.decode() if isinstance(proc.stdout, (bytes, bytearray)) else proc.stdout
            else:
                help_text = proc.stderr.decode() if proc.stderr else ""
            doc = help_text
        except Exception:
            doc = ""

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
    print(" [↑/↓]: Navigation  [F1]: Aide  [F2]: Options  [Enter]: Lancer  [F10]: Quitter")
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
