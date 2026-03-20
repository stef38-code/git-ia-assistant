"""Helpers pour le CLI de commit (rangés dans core/cli_helpers).

Contient :
- determiner_ia_choisie(parser, args)
- detecter_fichiers(args)
- handle_dry_run(args, parser, fichiers)
- generer_mcp_config(out_dir, langage, repo_path)
- handle_clear(out_dir)

Toutes les fonctions documentées en français.
"""

import os
from pathlib import Path
from typing import Iterable, List, Optional

from python_commun.logging import logger
from python_commun.git.git_core import liste_fichier_non_suivis_et_modifies
from python_commun.system.system import vide_repertoire
from git_ia_assistant.cli.mcp.mcp_config_manager import McpConfigManager


def determiner_ia_choisie(parser, args) -> str:
    """Détermine l'IA à utiliser (priorités) :
    1. variable d'environnement IA_SELECTED (ou IA) si valide (gemini,copilot,ollama)
    2. présence de GEMINI_API_KEY → 'gemini'
    3. présence de COPILOT_API_KEY ou GITHUB_TOKEN → 'copilot'
    4. sinon → 'ollama'
    """
    ia_defaut = parser.get_default("ia")
    ia_choisie = getattr(args, "ia", ia_defaut)
    if ia_choisie == ia_defaut:
        env_ia = os.getenv("IA_SELECTED") or os.getenv("IA")
        if env_ia and env_ia.lower() in ("gemini", "copilot", "ollama"):
            return env_ia.lower()
        # Priorité aux clés API
        if os.getenv("GEMINI_API_KEY"):
            return "gemini"
        if os.getenv("COPILOT_API_KEY") or os.getenv("GITHUB_TOKEN"):
            return "copilot"
        return "ollama"
    return ia_choisie


def detecter_fichiers(args) -> List[str]:
    """Retourne la liste des fichiers à traiter (argument -f ou fichiers git modifiés/non suivis)."""
    fichiers = getattr(args, "fichier", None)
    if fichiers:
        return fichiers
    return liste_fichier_non_suivis_et_modifies()


def handle_dry_run(args, parser, fichiers: Iterable[str]) -> None:
    """Comportement pour --dry-run : affiche l'IA choisie, vérifie rapidement MCP et liste les fichiers."""
    ia = determiner_ia_choisie(parser, args)
    logger.log_info(f"[DRY-RUN] IA sélectionnée : {ia}")
    # Vérification rapide (non exhaustive) pour éviter de bloquer l'utilisateur
    servers_ok = McpConfigManager.verifier_installation(servers=[])
    if servers_ok:
        logger.log_info("[DRY-RUN] Vérification rapide terminée (pas d'inspection complète).")
    else:
        logger.log_warn("[DRY-RUN] Problèmes détectés lors de la vérification rapide (voir erreurs).")
    logger.log_info(f"[DRY-RUN] Fichiers pris en compte : {list(fichiers)}")
    logger.log_info("[DRY-RUN] Pour une vérification complète, exécutez sans --dry-run.")


def generer_mcp_config(out_dir: Path, langage: str, repo_path: Path, plateforme: Optional[str] = None, token: Optional[str] = None) -> Path:
    """Génère la configuration MCP et retourne le chemin du fichier de config généré.

    - plateforme: si fourni, utilisé (ex: 'gitlab', 'github'), sinon 'local' par défaut
    - token: token Git (si nécessaire pour accéder aux dépôts distants)

    Encapsule l'appel à McpConfigManager.generer_config pour centraliser la logique.
    """
    out_dir = Path(out_dir)
    # S'assurer que le répertoire existe
    out_dir.mkdir(parents=True, exist_ok=True)

    params = {
        "out_dir": out_dir,
        "langage": langage,
        "repo_path": repo_path,
    }
    # platform et token sont optionnels et passés seulement si fournis
    params["plateforme"] = plateforme or "local"
    if token:
        params["token"] = token

    mcp_config_path = McpConfigManager.generer_config(**params)
    logger.log_info(f"MCP config générée: {mcp_config_path}")
    return mcp_config_path


def log_ia_info(ia_choisie: str) -> None:
    """Affiche des informations sur le modèle IA sélectionné (utile pour commit et review CLI)."""
    model_info = ""
    if ia_choisie == "gemini":
        model_info = os.getenv("GEMINI_MODEL") or "gemini-2.5-flash"
    elif ia_choisie == "ollama":
        model_info = os.getenv("OLLAMA_MODEL") or "(local ollama)"
    elif ia_choisie == "copilot":
        model_info = os.getenv("COPILOT_MODEL") or "(copilot)"
    logger.log_info(f"ℹ INFO:  IA sélectionnée : {ia_choisie} {('- model: ' + model_info) if model_info else ''}")


def start_mcp_manager(mcp_config_path: Path):
    """Démarre un McpClientManager à partir du chemin de config donné et renvoie le manager ou None en cas d'erreur."""
    try:
        from python_commun.ai.mcp_client_manager import McpClientManager
        mcp_manager = McpClientManager(mcp_config_path)
        mcp_manager.demarrer_serveurs()
        return mcp_manager
    except Exception as e:
        logger.log_warn(f"Erreur lors du démarrage des serveurs MCP : {e}")
        return None


def stop_mcp_manager(mcp_manager) -> None:
    """Arrête proprement le manager MCP s'il existe."""
    if not mcp_manager:
        return
    try:
        mcp_manager.arreter_serveurs()
    except Exception:
        pass
    logger.log_info("🔌 Arrêt des serveurs MCP terminé.")


def dry_run_check(args, parser, message: str = "") -> None:
    """Vérification pour --dry-run : affiche l'IA choisie, vérifie rapidement MCP et affiche un message personnalisé.

    message: chaîne affichée pour indiquer ce qui serait analysé (ex: URL de MR, liste de fichiers)
    """
    ia = determiner_ia_choisie(parser, args)
    logger.log_info(f"[DRY-RUN] IA sélectionnée : {ia}")
    servers_ok = McpConfigManager.verifier_installation(servers=[])
    if servers_ok:
        logger.log_info("[DRY-RUN] Vérification rapide terminée (pas d'inspection complète).")
    else:
        logger.log_warn("[DRY-RUN] Problèmes détectés lors de la vérification rapide (voir erreurs).")
    if message:
        logger.log_info(f"[DRY-RUN] {message}")
    logger.log_info("[DRY-RUN] Pour une vérification complète, exécutez sans --dry-run.")


def handle_clear(out_dir: Path) -> None:
    """Nettoie le répertoire de travail OUT_DIR via python_commun.system.system.vide_repertoire."""
    vide_repertoire(Path(out_dir), True, False)
    logger.log_info(f"Répertoire de travail {out_dir} nettoyé.")
