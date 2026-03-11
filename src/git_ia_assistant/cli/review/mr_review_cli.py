#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    mr_review_cli - Effectue la relecture d'une MR/PR avec l'IA choisie (Copilot, Gemini, Ollama).

DESCRIPTION
    Script Python pour relire une Merge Request (GitLab) ou Pull Request (GitHub) à l'aide d'une IA.
    Analyse les changements, génère un résumé et une checklist de relecture sauvegardés en Markdown.
    
    Le script :
    - Clone ou met à jour le dépôt distant
    - Génère le diff de la MR/PR
    - Calcule les statistiques des changements
    - Génère un document de revue complet avec analyse de l'IA

OPTIONS
    -u, --url URL               URL de la MR/PR (GitLab ou GitHub) (OBLIGATOIRE)
    -ia copilot|gemini|ollama   Choix de l'IA (défaut: auto-détecté via IA_SELECTED ou copilot)
    --dry-run                   Simulation, affiche le prompt sans appel à l'IA
    --publier                   Publier le rapport de revue comme commentaire dans la MR/PR
    -h, --help                  Afficher l'aide du script

EXEMPLES
    git-ia-mr -u https://gitlab.com/repo/-/merge_requests/1 --dry-run
    git-ia-mr -u https://github.com/user/repo/pull/456 -ia gemini
    git-ia-mr --url https://gitlab.com/org/project/-/merge_requests/123
    git-ia-mr -u https://gitlab.com/repo/-/merge_requests/1 --publier
"""

import argparse
import os
import sys
import urllib.request
import urllib.error
import urllib3
from pathlib import Path

# Désactiver les avertissements SSL pour les serveurs avec certificats auto-signés
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Ajout du chemin racine et de la librairie commune pour permettre l'import des modules du projet
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../libs/python_commun/src")))

from python_commun.vcs.mr_utils import cloner_ou_fetch_depot, generer_diff_mr, publier_commentaire_mr, verifier_droits_publication_mr
from python_commun.vcs.diff_stats import (
    calculer_stats_mr,
    ecrire_checklist_mr,
    ecrire_resume_mr,
    extraire_fichiers_modifies,
)
from python_commun.vcs.version_detection import extraire_toutes_versions
from python_commun.ai.ia_assistant_cli_utils import detecter_ia
from python_commun.logging import logger
from python_commun.system.system import vide_repertoire, detect_lang_and_framework
from python_commun.network.url_utils import (
    creer_url_ssh,
    rechercher_information_depuis_url,
)
from python_commun.cli.usage import usage
from git_ia_assistant.core.definition.ia_assistant_mr_factory import IaAssistantMrFactory

HOME = Path.home()
OUT_DIR = HOME / "ia_assistant/mrOrpr"

# Limites de tokens par IA (80% de la capacité maximale pour sécurité)
MAX_TOKENS_LIMITS = {
    'copilot': 100_000,   # GPT-4 Turbo : ~128K tokens max
    'gemini': 800_000,    # Gemini 1.5 Pro : ~1M tokens max
    'ollama': 50_000,     # Conservative pour compatibilité modèles
}

# Seuils d'avertissement (70% de la limite)
WARNING_THRESHOLDS = {
    'copilot': 70_000,
    'gemini': 560_000,
    'ollama': 35_000,
}


def estimer_tokens(texte: str) -> int:
    """
    Estime le nombre de tokens d'un texte (approximation : 1 token ≈ 4 caractères).
    
    :param texte: Le texte à analyser
    :return: Nombre estimé de tokens
    """
    return len(texte) // 4


def verifier_taille_mr(diff_path: Path, stats: dict, ia_utilisee: str) -> bool:
    """
    Vérifie si la taille de la MR est acceptable pour l'IA choisie.
    Affiche des avertissements et retourne False si trop volumineuse.
    
    :param diff_path: Chemin vers le fichier diff
    :param stats: Statistiques de la MR
    :param ia_utilisee: Nom de l'IA utilisée
    :return: True si OK, False si trop volumineux
    """
    # Lire le diff et estimer les tokens
    diff_content = diff_path.read_text(encoding='utf-8')
    tokens_estimés = estimer_tokens(diff_content)
    
    # Récupérer les limites pour cette IA
    max_tokens = MAX_TOKENS_LIMITS.get(ia_utilisee, 50_000)
    warn_threshold = WARNING_THRESHOLDS.get(ia_utilisee, 35_000)
    
    nb_fichiers = stats.get('fichiers_modifies', 0)
    nb_lignes = stats.get('additions', 0) + stats.get('suppressions', 0)
    
    # Affichage des statistiques
    logger.log_info("📊 Analyse de volumétrie :")
    logger.log_info(f"  • Fichiers modifiés : {nb_fichiers}")
    logger.log_info(f"  • Lignes changées : {nb_lignes:,}")
    logger.log_info(f"  • Tokens estimés : {tokens_estimés:,}")
    logger.log_info(f"  • Limite {ia_utilisee.capitalize()} : {max_tokens:,} tokens")
    
    # Vérification des seuils
    if tokens_estimés > max_tokens:
        logger.log_error(f"❌ MR trop volumineuse pour {ia_utilisee.capitalize()} !")
        logger.log_error(f"   Tokens estimés : {tokens_estimés:,} > Limite : {max_tokens:,}")
        logger.log_error("")
        logger.log_error("💡 Solutions possibles :")
        logger.log_error("   1. Utiliser Gemini avec -ia gemini (limite : 800K tokens)")
        logger.log_error("   2. Découper la MR en plusieurs MR plus petites")
        logger.log_error("   3. Exclure les fichiers générés (package-lock.json, dist/, etc.)")
        return False
    
    if tokens_estimés > warn_threshold:
        pourcentage = int((tokens_estimés / max_tokens) * 100)
        logger.log_warn(f"⚠️  MR volumineuse : {tokens_estimés:,} tokens ({pourcentage}% de la limite)")
        logger.log_warn(f"   Temps de traitement estimé : 2-5 minutes")
        
        if ia_utilisee == 'gemini':
            cout_estime = (tokens_estimés / 1_000_000) * 0.15
            logger.log_warn(f"   Coût estimé Gemini : ~${cout_estime:.3f}")
    
    return True


def _parser_options() -> argparse.Namespace:
    """
    Analyse les options de la ligne de commande.

    :return: Un objet Namespace contenant les arguments parsés.
    """
    parser = argparse.ArgumentParser(
        description="Relecture de MR/PR via IA", add_help=False
    )
    parser.add_argument("-h", "--help", action="store_true", help="Afficher l'aide.")
    parser.add_argument("-u", "--url", help="URL de la MR/PR à relire")
    parser.add_argument(
        "-ia",
        choices=["copilot", "gemini", "ollama"],
        default=None,
        help="Nom de l'IA à utiliser (défaut: auto-détection)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Simulation, affiche le prompt généré"
    )
    parser.add_argument(
        "--publier", 
        action="store_true", 
        help="Publier le rapport de revue comme commentaire dans la MR/PR"
    )
    return parser.parse_args()


def extraire_branches_mr(url: str, plateforme: str, espace_projet: str, numero_mr: int, token: str) -> tuple:
    """
    Extrait les branches source et target d'une MR/PR via l'API GitLab/GitHub.
    
    :param url: URL de la MR/PR
    :param plateforme: 'gitlab' ou 'github'
    :param espace_projet: Identifiant du projet (ex: 'groupe/projet')
    :param numero_mr: Numéro de la MR/PR
    :param token: Token d'authentification
    :return: Tuple (source_branch, target_branch)
    """
    try:
        if plateforme.lower() == "gitlab":
            import gitlab
            gitlab_url = "https://" + url.split("/")[2]
            gl = gitlab.Gitlab(url=gitlab_url, private_token=token, ssl_verify=False)
            gl.auth()
            project = gl.projects.get(espace_projet)
            mr = project.mergerequests.get(numero_mr)
            return mr.source_branch, mr.target_branch
        elif plateforme.lower() == "github":
            from github import Github
            g = Github(token)
            repo = g.get_repo(espace_projet)
            pr = repo.get_pull(numero_mr)
            return pr.head.ref, pr.base.ref
        else:
            logger.log_error(f"Plateforme non supportée: {plateforme}")
            return None, None
    except Exception as e:
        logger.log_error(f"Impossible d'extraire les branches depuis l'API: {e}")
        return None, None


def extraire_version_fichier(repo_path: Path, branche: str) -> dict:
    """
    Extrait les versions des différents langages/frameworks depuis les fichiers de configuration.
    
    :param repo_path: Chemin du dépôt local
    :param branche: Nom de la branche à analyser
    :return: Dict avec les versions trouvées {langage: version}
    """
    versions = {}
    
    try:
        import git
        repo = git.Repo(str(repo_path))
        
        # Checkout temporaire de la branche
        current_branch = repo.active_branch.name if repo.active_branch else None
        try:
            repo.git.checkout(branche)
        except Exception:
            # Impossible de checkout - retour d'un dict vide (silencieux)
            return versions
        
        # Extraction des versions via python_commun
        try:
            versions = extraire_toutes_versions(repo_path)
        except Exception:
            # Erreur lors de l'extraction - retour d'un dict vide (silencieux)
            pass
        
        # Retour à la branche d'origine
        if current_branch:
            try:
                repo.git.checkout(current_branch)
            except Exception:
                # Impossible de retourner à la branche - non critique
                pass
                
    except Exception:
        # Erreur générale (ex: pas un dépôt Git) - retour d'un dict vide (silencieux)
        pass
    
    return versions


def detecter_migration(repo_path: Path, source_branch: str, target_branch: str) -> dict:
    """
    Détecte les migrations de version entre les branches source et target.
    
    :param repo_path: Chemin du dépôt local
    :param source_branch: Branche source de la MR
    :param target_branch: Branche target de la MR
    :return: Dict avec {detected: bool, migrations: [...]}
    """
    if not source_branch or not target_branch:
        return {"detected": False, "migrations": []}
    
    logger.log_info(f"Détection de migration entre {source_branch} → {target_branch}")
    
    # Extraire les versions de chaque branche
    versions_source = extraire_version_fichier(repo_path, source_branch)
    versions_target = extraire_version_fichier(repo_path, target_branch)
    
    migrations = []
    
    # Comparer les versions
    all_langages = set(list(versions_source.keys()) + list(versions_target.keys()))
    
    for langage in all_langages:
        version_source = versions_source.get(langage)
        version_target = versions_target.get(langage)
        
        # Migration détectée si les versions diffèrent
        if version_source and version_target and version_source != version_target:
            migrations.append({
                "langage": langage,
                "version_source": version_target,  # target = ancienne version (avant merge)
                "version_target": version_source   # source = nouvelle version (après merge)
            })
        elif version_source and not version_target:
            # Suppression de version (rare mais possible)
            logger.log_info(f"Version {langage} supprimée : {version_source}")
        elif not version_source and version_target:
            # Ajout de version (nouveau langage dans le projet)
            logger.log_info(f"Version {langage} ajoutée : {version_target}")
    
    return {
        "detected": len(migrations) > 0,
        "migrations": migrations
    }


def _verifier_url_existe(url: str, token: str = None) -> bool:
    """
    Vérifie si une URL est accessible, en utilisant un token d'authentification si fourni.

    :param url: L'URL à vérifier.
    :param token: Le token d'authentification (pour les dépôts privés).
    :return: True si l'URL est accessible, False sinon.
    """
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        req = urllib.request.Request(url, headers=headers, method="HEAD")
        urllib.request.urlopen(req)
        return True
    except urllib.error.HTTPError as e:
        logger.log_error(f"L'URL a retourné une erreur HTTP {e.code}: {e.reason}")
        if e.code == 401:
            logger.log_error(
                "Erreur 401 Unauthorized. Votre token (GIT_TOKEN) est peut-être invalide ou manquant."
            )
        elif e.code == 404:
            logger.log_error("Erreur 404 Not Found. Vérifiez que l'URL est correcte.")
        return False
    except Exception as e:
        logger.log_error(f"Impossible de vérifier l'URL. Erreur : {e}")
        return False


def main() -> None:
    """
    Point d'entrée principal du script.
    """
    args = _parser_options()
    
    # Gestion de l'aide
    if getattr(args, "help", False):
        usage(__file__)
        return
    
    # Vérification de l'URL obligatoire
    if not args.url:
        logger.die("L'option -u/--url est obligatoire. Utilisez -h pour l'aide.")
    
    ia_utilisee = args.ia or detecter_ia()
    git_token = os.environ.get("GIT_TOKEN")
    
    # Vérification du token pour les dépôts GitLab/GitHub
    if not args.dry_run and not git_token:
        logger.die(
            "La variable d'environnement GIT_TOKEN n'est pas définie.\n"
            "Pour GitLab:\n"
            "  • Sans --publier: créez un token avec scopes 'read_api' + 'read_repository'\n"
            "  • Avec --publier: créez un token avec scope 'api' (écriture requise)\n"
            "Pour GitHub:\n"
            "  • Sans --publier: token avec scope 'public_repo' ou 'repo' (lecture)\n"
            "  • Avec --publier: token avec scope 'repo' (écriture requise)\n"
            "Puis exportez-le: export GIT_TOKEN='votre_token'"
        )

    if not args.dry_run and not _verifier_url_existe(args.url, git_token):
        logger.die("L'URL de la MR/PR est inaccessible. Arrêt du script.")

    plateforme, nom_projet, espace_projet, numero_merge = (
        rechercher_information_depuis_url(args.url)
    )
    if not all([plateforme, nom_projet, espace_projet, numero_merge]):
        logger.die("Impossible de parser les informations depuis l'URL.")

    # Vérification préalable des droits si --publier est activé
    if args.publier and not args.dry_run:
        logger.log_info("")
        logger.log_info("🔐 Vérification des droits du token pour publication...")
        
        has_rights, message = verifier_droits_publication_mr(
            plateforme=plateforme,
            espace_projet=espace_projet,
            url_mr=args.url,
            token=git_token
        )
        
        if not has_rights:
            logger.log_error(f"❌ Vérification des droits échouée: {message}")
            logger.log_error("")
            logger.log_error("La publication nécessite :")
            if plateforme.lower() == "gitlab":
                logger.log_error("  • GitLab : Token avec scope 'api' (accès complet)")
                logger.log_error(f"  • Créer token : https://{args.url.split('/')[2]}/-/user_settings/personal_access_tokens")
            else:
                logger.log_error("  • GitHub : Token avec scope 'repo' (accès complet)")
                logger.log_error("  • Créer token : https://github.com/settings/tokens")
            logger.log_error("")
            logger.log_error("💡 Astuce : Retirez l'option --publier pour générer uniquement le rapport local")
            logger.die("Arrêt : droits insuffisants pour publication")
        
        logger.log_info("")


    vide_repertoire(OUT_DIR, getattr(args, "clean_outdir", True), args.dry_run)

    depot_ssh = creer_url_ssh(args.url)
    # cloner_ou_fetch_depot construit le chemin final lui-même, on passe juste le répertoire de base
    cloner_ou_fetch_depot(depot_ssh, OUT_DIR, args.dry_run)
    repo_local_path = OUT_DIR / depot_ssh.split(":")[-1].replace(".git", "")

    fichier_diff = OUT_DIR / f"diff_{numero_merge}.patch"
    generer_diff_mr(
        out_dir=repo_local_path,
        numero_mr=numero_merge,
        fichier_diff=fichier_diff,
        dry_run=args.dry_run,
        plateforme=plateforme,
        espace_projet=espace_projet,
        url_mr=args.url,
        token=git_token,
    )

    fichier_liste_fichiers = OUT_DIR / f"files_{numero_merge}.txt"
    extraire_fichiers_modifies(fichier_diff, fichier_liste_fichiers)

    stats = calculer_stats_mr(fichier_diff, fichier_liste_fichiers)

    # Affichage du nombre de changements et de commits
    nb_fichiers = stats.get('fichiers_modifies', 0)
    nb_lignes_ajoutees = stats.get('additions', 0)
    nb_lignes_supprimees = stats.get('suppressions', 0)
    
    logger.log_info("Résumé des changements :")
    logger.log_info(f"  • Fichiers modifiés : {nb_fichiers}")
    logger.log_info(f"  • Lignes ajoutées : {nb_lignes_ajoutees}")
    logger.log_info(f"  • Lignes supprimées : {nb_lignes_supprimees}")

    fichier_resume = OUT_DIR / f"resume_{numero_merge}.md"
    ecrire_resume_mr(fichier_resume, numero_merge, stats, fichier_liste_fichiers)

    fichier_checklist = OUT_DIR / f"checklist_{numero_merge}.md"
    ecrire_checklist_mr(fichier_checklist, args.url)

    # Détection du langage et framework du projet
    langage_framework_base = detect_lang_and_framework(repo_local_path)
    
    # Détection de migration de version
    migration_info = {"detected": False, "migrations": []}
    if not args.dry_run:
        source_branch, target_branch = extraire_branches_mr(
            args.url, plateforme, espace_projet, numero_merge, git_token
        )
        if source_branch and target_branch:
            migration_info = detecter_migration(repo_local_path, source_branch, target_branch)
            
            # Affichage des informations de migration
            if migration_info.get("detected", False):
                logger.log_info("🔄 Migration détectée !")
                for mig in migration_info.get("migrations", []):
                    langage = mig.get("langage", "").upper()
                    version_ancienne = mig.get("version_source", "")  # source dans le dict = ancienne
                    version_nouvelle = mig.get("version_target", "")  # target dans le dict = nouvelle
                    logger.log_info(f"  • {langage}: {version_ancienne} → {version_nouvelle}")
            else:
                logger.log_info("ℹ️  Aucune migration de version détectée")
    else:
        logger.log_info("[Dry Run] Détection de migration ignorée en mode dry-run")

    # Extraction des versions actuelles du projet (toujours, même sans migration)
    versions_actuelles = {}
    try:
        versions_actuelles = extraire_toutes_versions(repo_local_path)
    except Exception:
        pass
    
    # Adapter le langage/framework pour indiquer la version de destination si migration
    langage_framework = langage_framework_base
    if migration_info.get("detected", False) and migration_info.get("migrations"):
        # Remplacer les versions source par les versions de destination dans le langage détecté
        for mig in migration_info.get("migrations", []):
            langage = mig.get("langage", "").lower()
            version_source = mig.get("version_source", "")
            version_target = mig.get("version_target", "")
            
            if version_source and version_target:
                # Extraire la version majeure (ex: "14.3" -> "14", "20.3" -> "20")
                import re
                match_source = re.match(r'(\d+)', version_source)
                match_target = re.match(r'(\d+)', version_target)
                
                if match_source and match_target:
                    version_majeure_source = match_source.group(1)
                    version_majeure_target = match_target.group(1)
                    
                    # Remplacer "Angular 14" par "Angular 20" (case-insensitive)
                    pattern = re.compile(rf'\b{langage}\s+{version_majeure_source}\b', re.IGNORECASE)
                    langage_framework = pattern.sub(f"{langage.capitalize()} {version_majeure_target}", langage_framework)
    
    logger.log_info(f"Langage/Framework détecté : {langage_framework}")

    # Vérification de la taille de la MR avant de générer la revue
    if not args.dry_run:
        if not verifier_taille_mr(fichier_diff, stats, ia_utilisee):
            logger.log_error("")
            logger.log_error("❌ Abandon de la génération de la revue en raison de la taille excessive.")
            return

    # Utilisation du pattern Factory pour instancier la classe IA appropriée
    ia_instance = IaAssistantMrFactory.create_mr_instance(
        ia=ia_utilisee,
        url_mr=args.url,
        plateforme=plateforme,
        numero_mr=numero_merge,
        out_dir=OUT_DIR,
        dry_run=args.dry_run,
        langage=langage_framework,
        migration_info=migration_info,
        versions_actuelles=versions_actuelles,
    )

    # Génération de la revue via l'IA
    result = ia_instance.generer_revue_mr(fichier_diff, fichier_resume)

    # En mode dry-run, la méthode retourne None après affichage
    if args.dry_run:
        return

    # Sauvegarde du résultat
    if result:
        md_path = OUT_DIR / f"mrOrpr_{espace_projet.replace('/', '_')}_{numero_merge}.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# Revue de la {plateforme} MR/PR !{numero_merge}\n\n{result}")
        logger.log_success(f"Document de revue généré : {md_path}")
        
        # Publication du commentaire si demandé
        if args.publier:
            logger.log_info("")
            logger.log_info("📤 Publication du rapport dans la MR/PR...")
            logger.log_info("⚠️  Vérification : Token doit avoir scope 'api' (GitLab) ou 'repo' (GitHub)")
            
            # Vérification du token pour la publication
            if not git_token:
                logger.log_error("Impossible de publier : GIT_TOKEN manquant")
                logger.log_info("Le rapport a été sauvegardé localement uniquement")
            else:
                # Préparation du commentaire avec header
                commentaire_header = f"# 🤖 Revue automatique par IA ({ia_utilisee.capitalize()})\n\n"
                commentaire_complet = commentaire_header + result
                
                # Publication
                success = publier_commentaire_mr(
                    numero_mr=numero_merge,
                    commentaire=commentaire_complet,
                    dry_run=False,  # args.dry_run est déjà False ici
                    plateforme=plateforme,
                    espace_projet=espace_projet,
                    url_mr=args.url,
                    token=git_token
                )
                
                if not success:
                    logger.log_error("La publication a échoué, mais le rapport local est disponible")
                    logger.log_info("")
                    logger.log_info("💡 Si l'erreur est '403: insufficient_scope' :")
                    if plateforme.lower() == "gitlab":
                        logger.log_info("   → Votre token a 'read_api' mais il faut 'api' pour publier")
                        logger.log_info(f"   → Créez un nouveau token : https://{args.url.split('/')[2]}/-/user_settings/personal_access_tokens")
                    else:
                        logger.log_info("   → Votre token doit avoir le scope 'repo' (pas seulement 'public_repo')")
                        logger.log_info("   → Créez un nouveau token : https://github.com/settings/tokens")
    else:
        logger.log_error("Échec de la génération de la revue.")


if __name__ == "__main__":
    main()
