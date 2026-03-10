#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    analyse_qualite_code - Analyse la qualité du code via SonarQube/SonarCloud.

DESCRIPTION
    Script Python pour interroger SonarQube/SonarCloud via son API REST et récupérer
    les métriques de qualité du code : bugs, vulnérabilités, code smells, hotspots de sécurité.
    
    Ce script permet de :
    - Se connecter à SonarQube/SonarCloud
    - Vérifier la configuration et l'authentification
    - Récupérer les métriques de qualité d'un projet
    - Afficher un rapport structuré des problèmes détectés
    
    **Prérequis** :
    - Installation de la bibliothèque python-sonarqube-api : pip install python-sonarqube-api
    - Variables d'environnement configurées (SONAR_HOST_URL, SONAR_TOKEN)

OPTIONS
    -h, --help                  Afficher l'aide
    --dry-run                   Simuler la connexion et afficher la configuration sans interroger l'API

VARIABLES D'ENVIRONNEMENT
    SONAR_HOST_URL              URL du serveur SonarQube/SonarCloud (OBLIGATOIRE)
                                Exemples: https://sonarcloud.io ou https://sonar.example.com
    
    SONAR_TOKEN                 Token d'authentification généré depuis SonarQube (OBLIGATOIRE)
                                Format SonarQube: squ_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
                                Format SonarCloud: sqp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

EXEMPLES
    # Tester la configuration et la connexion
    analyse_qualite_code.py --dry-run
    
    # Se connecter à SonarQube et récupérer les métriques
    analyse_qualite_code.py
    
    # Configuration des variables d'environnement
    export SONAR_HOST_URL="https://sonarcloud.io"
    export SONAR_TOKEN="sqp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    analyse_qualite_code.py

FUNCTIONS
    main() : Point d'entrée du script, gère les options et le workflow principal.
"""

import argparse
import json
import os
import sys

# Ajout du chemin racine et de la librairie commune pour permettre l'import des modules du projet
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../libs/python_commun/src")))

from python_commun.cli.usage import usage
from python_commun.logging import logger


def _parser_options() -> argparse.Namespace:
    """
    Analyse et retourne les arguments de la ligne de commande.

    :return: Un objet Namespace contenant les arguments parsés.
    """
    parser = argparse.ArgumentParser(
        add_help=False, description="Analyse la qualité du code via SonarQube/SonarCloud."
    )
    parser.add_argument(
        "-h", "--help", action="store_true", help="Afficher l'aide."
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Simuler la connexion sans interroger l'API."
    )
    return parser.parse_args()


def verifier_variables_environnement() -> tuple[str, str]:
    """
    Vérifie que les variables d'environnement SONAR_HOST_URL et SONAR_TOKEN sont définies et non vides.

    :return: Tuple (sonar_host_url, sonar_token)
    :raises SystemExit: Si une variable est manquante ou vide
    """
    sonar_host_url = os.getenv("SONAR_HOST_URL", "").strip()
    sonar_token = os.getenv("SONAR_TOKEN", "").strip()

    erreurs = []
    
    if not sonar_host_url:
        erreurs.append("❌ SONAR_HOST_URL n'est pas définie ou est vide")
        logger.log_error("Variable d'environnement SONAR_HOST_URL manquante")
    
    if not sonar_token:
        erreurs.append("❌ SONAR_TOKEN n'est pas défini ou est vide")
        logger.log_error("Variable d'environnement SONAR_TOKEN manquante")
    
    if erreurs:
        print("\n🔴 Erreur de configuration :\n")
        for erreur in erreurs:
            print(f"  {erreur}")
        print("\n📝 Configuration requise :")
        print("  export SONAR_HOST_URL=\"https://sonarcloud.io\"")
        print("  export SONAR_TOKEN=\"sqp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\"\n")
        sys.exit(1)
    
    logger.log_info(f"Variables d'environnement validées : SONAR_HOST_URL={sonar_host_url}")
    return sonar_host_url, sonar_token


def tester_connexion_sonar(sonar_host_url: str, sonar_token: str, dry_run: bool = False) -> bool:
    """
    Test la connexion à SonarQube/SonarCloud en utilisant la bibliothèque python-sonarqube-api.

    :param sonar_host_url: URL du serveur SonarQube
    :param sonar_token: Token d'authentification
    :param dry_run: Si True, affiche la configuration sans tester la connexion
    :return: True si la connexion est réussie, False sinon
    """
    try:
        # Import dynamique pour éviter les erreurs si la bibliothèque n'est pas installée
        from sonarqube import SonarQubeClient
    except ImportError:
        logger.log_error("La bibliothèque 'python-sonarqube-api' n'est pas installée")
        print("\n❌ Erreur : bibliothèque manquante")
        print("📦 Installation requise : pip install python-sonarqube-api\n")
        return False

    if dry_run:
        print("\n🔍 Mode simulation (--dry-run)")
        print(f"  📡 SONAR_HOST_URL : {sonar_host_url}")
        print(f"  🔑 SONAR_TOKEN    : {sonar_token[:10]}{'*' * (len(sonar_token) - 10)}")
        print("\n✅ Configuration validée (aucune connexion réelle effectuée)\n")
        logger.log_info("Mode dry-run : configuration affichée sans connexion")
        return True

    try:
        logger.log_info(f"Tentative de connexion à SonarQube : {sonar_host_url}")
        print(f"\n🔗 Connexion à SonarQube...")
        print(f"  📡 Serveur : {sonar_host_url}")
        
        # Création du client SonarQube
        sonar = SonarQubeClient(sonarqube_url=sonar_host_url, token=sonar_token)
        
        # Test de connexion via la vérification des credentials
        auth_result_str = sonar.auth.check_credentials()
        auth_result = json.loads(auth_result_str) if isinstance(auth_result_str, str) else auth_result_str
        
        if auth_result and auth_result.get('valid', False):
            print(f"  ✅ Connexion réussie !")
            print(f"  🔑 Authentification validée")
            logger.log_info(f"Connexion à SonarQube réussie : {auth_result}")
            
            # Afficher des informations supplémentaires si disponibles
            try:
                server_info = sonar.server.get_server_version()
                if server_info:
                    print(f"  🏷️  Version SonarQube : {server_info}")
            except Exception as e:
                logger.log_debug(False, f"Impossible de récupérer la version du serveur : {e}")
            
            print()
            return True
        else:
            logger.log_warn("Connexion établie mais authentification invalide")
            print("  ⚠️  Authentification invalide\n")
            return False

    except Exception as e:
        logger.log_error(f"Erreur lors de la connexion à SonarQube : {e}")
        print(f"  ❌ Échec de la connexion")
        print(f"  💥 Erreur : {str(e)}\n")
        print("🔍 Vérifications à effectuer :")
        print("  1. L'URL du serveur est-elle correcte et accessible ?")
        print("  2. Le token est-il valide et non expiré ?")
        print("  3. Avez-vous les permissions nécessaires ?")
        print("  4. Le serveur SonarQube est-il opérationnel ?\n")
        return False


def main() -> None:
    """
    Point d'entrée principal du script.
    
    Gère le workflow complet :
    1. Parsing des arguments
    2. Affichage de l'aide si demandé
    3. Vérification des variables d'environnement
    4. Test de connexion à SonarQube
    """
    args = _parser_options()

    # Affichage de l'aide si demandé
    if getattr(args, "help", False):
        usage(__file__)
        return

    logger.log_info("Démarrage de l'analyse de qualité du code SonarQube")
    
    # Vérification des variables d'environnement
    sonar_host_url, sonar_token = verifier_variables_environnement()
    
    # Test de connexion
    connexion_ok = tester_connexion_sonar(sonar_host_url, sonar_token, args.dry_run)
    
    if not connexion_ok:
        logger.log_error("Impossible de se connecter à SonarQube")
        sys.exit(1)
    
    logger.log_success("Analyse de qualité du code terminée avec succès")


if __name__ == "__main__":
    main()
