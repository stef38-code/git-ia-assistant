#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    ollama-install-user-only - Script d'installation d'Ollama pour l'utilisateur courant.

DESCRIPTION
    Ce script permet d'installer, mettre à jour ou supprimer Ollama dans le
    répertoire personnel de l'utilisateur (~/.local/). Il gère également la
    configuration des variables d'environnement et des alias associés à Ollama.

FUNCTIONS
    recuperer_version_locale() -> Optional[str]
        Récupère la version d'Ollama installée localement.
    recuperer_derniere_version() -> Optional[str]
        Récupère la dernière version d'Ollama disponible sur GitHub.
    _configurer_environnement(simulation: bool = False) -> None
        Configure les variables d'environnement dans les fichiers RC.
    _nettoyer_environnement(simulation: bool = False) -> None
        Supprime les variables d'environnement des fichiers RC.
    _verifier_versions() -> bool
        Vérifie les versions locale et distante d'Ollama.
    _telecharger_et_extraire(prefixe: str, simulation: bool) -> bool
        Gère le téléchargement et l'extraction de l'archive Ollama.
    _finaliser_installation(prefixe: str, simulation: bool) -> None
        Gère les droits, l'environnement et les alias après l'installation.
    installer_ollama(simulation: bool = False) -> None
        Installe ou met à jour Ollama.
    _arreter_serveur(prefixe: str, simulation: bool) -> None
        Arrête le serveur Ollama si en cours d'exécution.
    _supprimer_fichiers_et_dossiers(prefixe: str, simulation: bool) -> None
        Supprime les binaires, bibliothèques et répertoires de configuration d'Ollama.
    _nettoyer_configuration(simulation: bool) -> None
        Supprime les variables d'environnement et les alias Ollama.
    supprimer_ollama(simulation: bool = False) -> None
        Supprime Ollama et nettoie la configuration.
    main() -> None
        Point d'entrée principal du script.

DATA
    ARCHIVE_URL: str
        URL de l'archive d'installation d'Ollama.
    LOCAL_DIR: Path
        Répertoire local d'installation (~/.local).
    BIN_DIR: Path
        Répertoire des binaires (~/.local/bin).
    LIB_DIR: Path
        Répertoire des bibliothèques (~/.local/lib).
    OLLAMA_BIN: Path
        Chemin vers l'exécutable Ollama.
    OLLAMA_LIB: Path
        Chemin vers les bibliothèques Ollama.
    ARCHIVE_PATH: Path
        Chemin temporaire de l'archive téléchargée.
    OLLAMA_CONFIG_DIR: Path
        Répertoire de configuration d'Ollama (~/.ollama).
    __all__ = ["installer_ollama", "supprimer_ollama"]
"""

import argparse
import re
import shutil
import sys
import urllib.request
from pathlib import Path
from typing import Optional

# Ajout du chemin racine pour l'import des modules commun
sys.path.append(str(Path(__file__).parents[2]))

from python_commun.installation import (
    ajouter_alias,
    determiner_fichiers_rc,
    modifier_fichier_rc,
    supprimer_alias,
    supprimer_ligne_fichier_rc,
)
from python_commun.logger import (
    log_debug,
    log_error,
    log_info,
    log_success,
    log_warn,
)
from python_commun.system import (
    executer_capture,
    executer_commande,
    verifier_commande,
)

# Constantes globales
ARCHIVE_URL: str = "https://ollama.com/download/ollama-linux-amd64.tar.zst"
LOCAL_DIR: Path = Path.home() / ".local"
BIN_DIR: Path = LOCAL_DIR / "bin"
LIB_DIR: Path = LOCAL_DIR / "lib"
OLLAMA_BIN: Path = BIN_DIR / "ollama"
OLLAMA_LIB: Path = LIB_DIR / "ollama"
ARCHIVE_PATH: Path = Path.home() / "ollama-linux-amd64.tar.zst"
OLLAMA_CONFIG_DIR: Path = Path.home() / ".ollama"

__all__ = ["installer_ollama", "supprimer_ollama"]


def recuperer_version_locale() -> Optional[str]:
    """
    Récupère la version d'Ollama installée localement.

    :return: Le numéro de version (ex: '0.15.1') ou None si non installé.
    """
    if not OLLAMA_BIN.exists():
        return None

    try:
        # On vérifie si le fichier est un binaire valide (pas un fichier texte "Not Found")
        # On lit les premiers octets pour vérifier le nombre magique ELF (\x7fELF)
        with open(OLLAMA_BIN, "rb") as f:
            debut = f.read(4)
            if debut != b"\x7fELF":
                log_debug(
                    True, f"Le fichier {OLLAMA_BIN} n'est pas un binaire ELF valide."
                )
                return None

        # ollama version affiche "ollama version is 0.5.7"
        resultat = executer_capture([str(OLLAMA_BIN), "--version"])
        sortie = resultat.stdout.strip()
        # On essaie d'extraire la version
        match = re.search(r"(\d+\.\d+\.\d+)", sortie)
        if match:
            return match.group(1)
        return None
    except OSError as e:
        # Capture spécifiquement l'erreur de format d'exécution (Exec format error)
        log_debug(True, f"Erreur système lors de l'exécution de {OLLAMA_BIN} : {e}")
        return None
    except Exception as erreur:
        log_debug(
            True, f"Erreur lors de la récupération de la version locale : {erreur}"
        )
        return None


def recuperer_derniere_version() -> Optional[str]:
    """
    Récupère la dernière version disponible sur GitHub via les redirections.

    :return: Le numéro de version (ex: '0.15.1') ou None en cas d'erreur.
    """
    url_latest = "https://github.com/ollama/ollama/releases/latest"
    try:
        # On utilise une requête HEAD pour suivre les redirections sans télécharger le contenu
        req = urllib.request.Request(url_latest, method="HEAD")
        with urllib.request.urlopen(req) as reponse:
            url_finale = reponse.geturl()
            # L'URL finale est de la forme https://github.com/ollama/ollama/releases/tag/v0.15.1
            match = re.search(r"tag/v?(\d+\.\d+\.\d+)", url_finale)
            if match:
                return match.group(1)
    except Exception as erreur:
        log_warn(f"Impossible de récupérer la dernière version sur GitHub : {erreur}")

    return None


def _configurer_environnement(simulation: bool = False) -> None:
    """
    Configure les variables d'environnement dans les fichiers RC.

    :param simulation: Si True, ne modifie rien.
    """
    variables_env = [
        ('export PATH="$HOME/.local/bin:$PATH"', "PATH"),
        (
            'export LD_LIBRARY_PATH="$HOME/.local/lib/ollama:$LD_LIBRARY_PATH"',
            "LD_LIBRARY_PATH",
        ),
        ('export OLLAMA_MODELS="$HOME/.ollama/models"', "OLLAMA_MODELS"),
    ]

    for ligne, desc in variables_env:
        motif = ligne.split("=")[0]
        modifier_fichier_rc(
            motif,
            ligne,
            f"variable d'environnement {desc}",
            simulation=simulation,
            commentaire_automatique=False,
        )


def _nettoyer_environnement(simulation: bool = False) -> None:
    """
    Supprime les variables d'environnement des fichiers RC.

    :param simulation: Si True, ne modifie rien.
    """
    variables_env = [
        ("export LD_LIBRARY_PATH=", "LD_LIBRARY_PATH"),
        ("export OLLAMA_MODELS=", "OLLAMA_MODELS"),
    ]

    for motif, desc in variables_env:
        supprimer_ligne_fichier_rc(
            motif, f"variable d'environnement {desc}", simulation=simulation
        )

    # Pour PATH, on cible spécifiquement la ligne Ollama
    supprimer_ligne_fichier_rc(
        'export PATH="$HOME/.local/bin:$PATH"',
        "entrée PATH Ollama",
        simulation=simulation,
    )


def _verifier_versions() -> bool:
    """
    Vérifie les versions locale et distante pour déterminer si une installation
    est nécessaire.

    :return: True si l'installation doit continuer, False sinon.
    """
    version_locale = recuperer_version_locale()
    version_distante = recuperer_derniere_version()

    if version_locale:
        log_info(f"Version locale détectée : {version_locale}")
        if version_distante:
            log_info(f"Dernière version disponible : {version_distante}")
            if version_locale == version_distante:
                log_success("Ollama est déjà à jour.")
                return False
            log_info(
                f"Une nouvelle version ({version_distante}) est disponible. Mise à jour..."
            )
        else:
            log_warn(
                "Impossible de vérifier la version distante. Installation forcée..."
            )
    else:
        log_info("Ollama n'est pas installé. Installation en cours...")

    return True


def _telecharger_et_extraire(prefixe: str, simulation: bool) -> bool:
    """
    Gère le téléchargement et l'extraction de l'archive Ollama.

    :param prefixe: Préfixe pour les messages de log (ex: '[SIMULATION]').
    :param simulation: Si True, simule les actions.
    :return: True si réussi, False sinon.
    """
    # 1. Vérifications préliminaires
    log_info(f"{prefixe}Vérification des dépendances...")
    if not verifier_commande("zstd"):
        log_error(
            "L'outil 'zstd' est requis pour la décompression. "
            "Veuillez l'installer (ex: sudo apt install zstd)."
        )
        return False

    # 2. Téléchargement
    log_info(f"{prefixe}Téléchargement de la dernière version d'Ollama...")
    if not simulation:
        try:
            urllib.request.urlretrieve(ARCHIVE_URL, ARCHIVE_PATH)
            log_success("Téléchargement terminé.")
        except Exception as e:
            log_error(f"Erreur lors du téléchargement : {e}")
            return False
    else:
        log_info(f"{prefixe}Téléchargement simulé depuis {ARCHIVE_URL}")

    # 3. Extraction
    log_info(f"{prefixe}Extraction vers {LOCAL_DIR}...")
    if not simulation:
        LOCAL_DIR.mkdir(parents=True, exist_ok=True)
        try:
            executer_commande(
                ["tar", "--zstd", "-xf", str(ARCHIVE_PATH), "-C", str(LOCAL_DIR)]
            )
            log_success("Extraction réussie.")
        except Exception as e:
            log_error(f"Erreur lors de l'extraction : {e}")
            return False
    else:
        log_info(f"{prefixe}Extraction simulée de {ARCHIVE_PATH} vers {LOCAL_DIR}")

    return True


def _finaliser_installation(prefixe: str, simulation: bool) -> None:
    """
    Gère les droits, l'environnement et les alias.

    :param prefixe: Préfixe pour les messages de log (ex: '[SIMULATION]').
    :param simulation: Si True, simule les actions.
    """
    # 4. Droits d'exécution
    if not simulation:
        if OLLAMA_BIN.exists():
            OLLAMA_BIN.chmod(OLLAMA_BIN.stat().st_mode | 0o111)
    else:
        log_info(f"{prefixe}Attribution des droits d'exécution sur {OLLAMA_BIN}")

    # 5. Configuration des variables d'environnement
    log_info(f"{prefixe}Configuration de l'environnement...")
    _configurer_environnement(simulation=simulation)

    # 6. Ajout des alias
    log_info(f"{prefixe}Configuration des alias...")
    cmd_demarrage = "nohup ollama serve > ~/.ollama/server.log 2>&1 &"
    ajouter_alias("ollama-start", cmd_demarrage, simulation=simulation)

    cmd_arret = "pkill ollama"
    ajouter_alias("ollama-stop", cmd_arret, simulation=simulation)

    log_success(f"{prefixe}Installation/Mise à jour d'Ollama terminée avec succès !")
    if not simulation:
        rc_files = determiner_fichiers_rc()
        fichiers_str = " ou ".join([f"source ~/{f.name}" for f in rc_files])
        log_info(
            f"Veuillez redémarrer votre terminal ou lancer '{fichiers_str}' "
            "pour appliquer les changements."
        )


def installer_ollama(simulation: bool = False) -> None:
    """
    Installe ou met à jour Ollama.

    :param simulation: Si True, simule les actions.
    """
    prefixe = "[SIMULATION] " if simulation else ""

    if not _verifier_versions():
        return

    try:
        if not _telecharger_et_extraire(prefixe, simulation):
            return

        _finaliser_installation(prefixe, simulation)

    finally:
        # Nettoyage
        if ARCHIVE_PATH.exists():
            log_info(f"{prefixe}Nettoyage du fichier temporaire {ARCHIVE_PATH}...")
            if not simulation:
                ARCHIVE_PATH.unlink()


def _arreter_serveur(prefixe: str, simulation: bool) -> None:
    """
    Arrête le serveur Ollama si celui-ci est en cours d'exécution.

    :param prefixe: Préfixe pour les messages de log (ex: '[SIMULATION]').
    :param simulation: Si True, simule l'action.
    """
    log_info(f"{prefixe}Arrêt du serveur Ollama si en cours...")
    if not simulation:
        try:
            executer_commande(["pkill", "ollama"], check=False)
        except Exception:
            pass


def _supprimer_fichiers_et_dossiers(prefixe: str, simulation: bool) -> None:
    """
    Supprime les binaires, bibliothèques et répertoires de configuration.

    :param prefixe: Préfixe pour les messages de log (ex: '[SIMULATION]').
    :param simulation: Si True, simule l'action.
    """
    fichiers_a_supprimer = [OLLAMA_BIN]
    dossiers_a_supprimer = [OLLAMA_LIB, OLLAMA_CONFIG_DIR]

    for f in fichiers_a_supprimer:
        if f.exists():
            log_info(f"{prefixe}Suppression du fichier {f}")
            if not simulation:
                f.unlink()

    for d in dossiers_a_supprimer:
        if d.exists():
            log_info(f"{prefixe}Suppression du dossier {d}")
            if not simulation:
                shutil.rmtree(d)


def _nettoyer_configuration(simulation: bool) -> None:
    """
    Supprime les variables d'environnement et les alias.

    :param simulation: Si True, simule l'action.
    """
    # Nettoyage de l'environnement
    log_info(
        f"{'[SIMULATION] ' if simulation else ''}Nettoyage des variables d'environnement..."
    )
    _nettoyer_environnement(simulation=simulation)

    # Suppression des alias
    log_info(f"{'[SIMULATION] ' if simulation else ''}Suppression des alias...")
    supprimer_alias("ollama-start", simulation=simulation)
    supprimer_alias("ollama-stop", simulation=simulation)


def supprimer_ollama(simulation: bool = False) -> None:
    """
    Supprime Ollama et nettoie la configuration.

    :param simulation: Si True, simule les actions.
    """
    prefixe = "[SIMULATION] " if simulation else ""
    log_info(f"{prefixe}Suppression d'Ollama...")

    # 1. Arrêt du serveur
    _arreter_serveur(prefixe, simulation)

    # 2. Suppression des fichiers
    _supprimer_fichiers_et_dossiers(prefixe, simulation)

    # 3. & 4. Nettoyage config et alias
    _nettoyer_configuration(simulation)

    log_success(f"{prefixe}Désinstallation d'Ollama terminée.")


def main() -> None:
    """
    Point d'entrée principal du script.
    """
    analyseur = argparse.ArgumentParser(
        description="Installateur Ollama pour l'utilisateur courant."
    )
    analyseur.add_argument(
        "--dry-run", action="store_true", help="Simuler les actions sans les exécuter."
    )
    analyseur.add_argument(
        "-r",
        "--remove",
        action="store_true",
        help="Supprimer Ollama et nettoyer la configuration.",
    )

    args = analyseur.parse_args()

    if args.remove:
        supprimer_ollama(simulation=args.dry_run)
    else:
        installer_ollama(simulation=args.dry_run)


if __name__ == "__main__":
    main()
