#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAME
    diagnose_gitlab_auth - Diagnostique l'authentification GitLab pour git-ia-mr.

DESCRIPTION
    Script de diagnostic pour tester la connexion et l'authentification à une instance GitLab.
    Permet de vérifier que le token GIT_TOKEN est valide et a les bonnes permissions.
    
    Ce script teste :
    - La connexion à l'instance GitLab
    - L'authentification avec le token fourni
    - L'accès à un projet spécifique (optionnel)
    - L'accès à une Merge Request spécifique (optionnel)

OPTIONS
    -u, --url URL           URL de l'instance GitLab (ex: https://gitlab.com)
    -p, --project PATH      Chemin du projet GitLab (ex: groupe/projet)
    -m, --mr NUMBER         Numéro de la Merge Request à tester
    -t, --token TOKEN       Token GitLab (utilise GIT_TOKEN si non fourni)
    --no-ssl-verify         Désactiver la vérification SSL
    -h, --help              Afficher l'aide

EXEMPLES
    # Test de connexion simple
    diagnose_gitlab_auth.py -u https://gitlab.com

    # Test avec un projet spécifique
    diagnose_gitlab_auth.py -u https://gitlab.com -p mygroup/myproject

    # Test complet avec projet et MR
    diagnose_gitlab_auth.py -u https://gitlab.com -p mygroup/myproject -m 123

    # Test avec un serveur GitLab privé (sans vérification SSL)
    diagnose_gitlab_auth.py -u https://gitlab.example.com --no-ssl-verify

    # Test avec un token spécifique (sinon utilise $GIT_TOKEN)
    diagnose_gitlab_auth.py -u https://gitlab.com -t glpat-xxxxxxxxxxxx
"""

import argparse
import os
import sys
import warnings

# Désactiver les warnings SSL si demandé
warnings.filterwarnings('ignore', message='Unverified HTTPS request')


def _parser_options() -> argparse.Namespace:
    """Parse les arguments de la ligne de commande."""
    parser = argparse.ArgumentParser(
        description="Diagnostic d'authentification GitLab",
        add_help=False
    )
    parser.add_argument(
        "-h", "--help", 
        action="store_true", 
        help="Afficher l'aide"
    )
    parser.add_argument(
        "-u", "--url",
        required=False,
        help="URL de l'instance GitLab (ex: https://gitlab.com)"
    )
    parser.add_argument(
        "-p", "--project",
        help="Chemin du projet GitLab (ex: groupe/sous-groupe/projet)"
    )
    parser.add_argument(
        "-m", "--mr",
        type=int,
        help="Numéro de la Merge Request à tester"
    )
    parser.add_argument(
        "-t", "--token",
        help="Token GitLab (utilise GIT_TOKEN si non fourni)"
    )
    parser.add_argument(
        "--no-ssl-verify",
        action="store_true",
        help="Désactiver la vérification SSL (pour certificats auto-signés)"
    )
    return parser.parse_args()


def afficher_aide():
    """Affiche l'aide du script."""
    print(__doc__)


def test_gitlab_auth(gitlab_url: str, token: str, ssl_verify: bool = True) -> bool:
    """
    Teste l'authentification GitLab avec le token fourni.
    
    :param gitlab_url: URL de l'instance GitLab
    :param token: Token d'authentification
    :param ssl_verify: Vérifier le certificat SSL
    :return: True si l'authentification réussit, False sinon
    """
    print("=" * 70)
    print(f"TEST 1: Connexion à {gitlab_url}")
    print("=" * 70)
    
    try:
        import gitlab
        
        # Connexion à GitLab
        gl = gitlab.Gitlab(
            url=gitlab_url,
            private_token=token,
            ssl_verify=ssl_verify
        )
        
        ssl_status = "activée" if ssl_verify else "désactivée"
        print(f"✅ Connexion créée (vérification SSL {ssl_status})")
        
        # Test d'authentification
        try:
            gl.auth()
            user = gl.user
            print(f"✅ Authentification réussie!")
            print(f"   Utilisateur: {user.username}")
            if hasattr(user, 'email'):
                print(f"   Email: {user.email}")
            print(f"   ID: {user.id}")
            return True
            
        except gitlab.exceptions.GitlabAuthenticationError as e:
            print(f"❌ Erreur d'authentification: {e}")
            print("\n⚠️  Possibilités:")
            print("  1. Le token est expiré")
            print("  2. Le token n'a pas les bons scopes (requis: read_api)")
            print("  3. Le token a été révoqué")
            print(f"\n💡 Vérifiez votre token sur: {gitlab_url}/-/profile/personal_access_tokens")
            return False
            
        except Exception as e:
            print(f"❌ Erreur inattendue: {type(e).__name__}: {e}")
            return False
            
    except ImportError:
        print("❌ Le module 'python-gitlab' n'est pas installé")
        print("   Installez-le avec: pip install python-gitlab")
        return False
    
    except Exception as e:
        print(f"❌ Erreur lors de la connexion: {type(e).__name__}: {e}")
        return False


def test_project_access(gitlab_url: str, token: str, project_path: str, ssl_verify: bool = True) -> bool:
    """
    Teste l'accès à un projet GitLab spécifique.
    
    :param gitlab_url: URL de l'instance GitLab
    :param token: Token d'authentification
    :param project_path: Chemin du projet (ex: groupe/projet)
    :param ssl_verify: Vérifier le certificat SSL
    :return: True si l'accès réussit, False sinon
    """
    print("\n" + "=" * 70)
    print(f"TEST 2: Accès au projet {project_path}")
    print("=" * 70)
    
    try:
        import gitlab
        
        gl = gitlab.Gitlab(
            url=gitlab_url,
            private_token=token,
            ssl_verify=ssl_verify
        )
        gl.auth()
        
        # Test d'accès au projet
        print(f"Tentative d'accès au projet: {project_path}")
        
        try:
            project = gl.projects.get(project_path)
            print(f"✅ Projet trouvé: {project.name}")
            print(f"   ID: {project.id}")
            print(f"   Description: {project.description[:100] if project.description else 'N/A'}...")
            print(f"   Visibilité: {project.visibility}")
            print(f"   URL: {project.web_url}")
            return True
            
        except gitlab.exceptions.GitlabGetError as e:
            print(f"❌ Impossible d'accéder au projet: {e}")
            print("\n⚠️  Vérifiez que:")
            print("  1. Le chemin du projet est correct (groupe/sous-groupe/nom)")
            print("  2. Votre token a accès à ce projet")
            print("  3. Le projet existe et n'est pas supprimé")
            return False
            
        except Exception as e:
            print(f"❌ Erreur inattendue: {type(e).__name__}: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_mr_access(gitlab_url: str, token: str, project_path: str, mr_number: int, ssl_verify: bool = True) -> bool:
    """
    Teste l'accès à une Merge Request spécifique.
    
    :param gitlab_url: URL de l'instance GitLab
    :param token: Token d'authentification
    :param project_path: Chemin du projet
    :param mr_number: Numéro de la MR
    :param ssl_verify: Vérifier le certificat SSL
    :return: True si l'accès réussit, False sinon
    """
    print("\n" + "=" * 70)
    print(f"TEST 3: Accès à la Merge Request !{mr_number}")
    print("=" * 70)
    
    try:
        import gitlab
        
        gl = gitlab.Gitlab(
            url=gitlab_url,
            private_token=token,
            ssl_verify=ssl_verify
        )
        gl.auth()
        
        # Accès au projet
        project = gl.projects.get(project_path)
        
        # Test d'accès à la MR
        print(f"Tentative d'accès à la MR #{mr_number}")
        
        try:
            mr = project.mergerequests.get(mr_number)
            print(f"✅ MR trouvée: {mr.title}")
            print(f"   État: {mr.state}")
            print(f"   Auteur: {mr.author['username']}")
            print(f"   Créée le: {mr.created_at}")
            print(f"   Branche source: {mr.source_branch}")
            print(f"   Branche cible: {mr.target_branch}")
            print(f"   URL: {mr.web_url}")
            return True
            
        except gitlab.exceptions.GitlabGetError as e:
            print(f"❌ Impossible d'accéder à la MR: {e}")
            print("\n⚠️  Vérifiez que:")
            print("  1. Le numéro de MR est correct")
            print("  2. La MR existe dans ce projet")
            print("  3. Vous avez les droits d'accès à cette MR")
            return False
            
        except Exception as e:
            print(f"❌ Erreur inattendue: {type(e).__name__}: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def main():
    """Point d'entrée principal du script."""
    args = _parser_options()
    
    # Affichage de l'aide
    if args.help:
        afficher_aide()
        return
    
    # Vérification de l'URL
    if not args.url:
        print("❌ ERREUR: L'option -u/--url est obligatoire")
        print("\nUtilisation:")
        print("  python diagnose_gitlab_auth.py -u https://gitlab.com")
        print("  python diagnose_gitlab_auth.py -h  # Pour l'aide complète")
        sys.exit(1)
    
    # Récupération du token
    token = args.token or os.environ.get("GIT_TOKEN")
    
    if not token:
        print("❌ ERREUR: Aucun token fourni")
        print("\nDeux options:")
        print("  1. Définir la variable d'environnement: export GIT_TOKEN='votre_token'")
        print("  2. Utiliser l'option -t: python diagnose_gitlab_auth.py -u ... -t 'votre_token'")
        sys.exit(1)
    
    print("\n🔍 DIAGNOSTIC D'AUTHENTIFICATION GITLAB\n")
    print(f"URL GitLab: {args.url}")
    print(f"Token: {token[:10]}... ({len(token)} caractères)")
    if args.project:
        print(f"Projet: {args.project}")
    if args.mr:
        print(f"Merge Request: #{args.mr}")
    print()
    
    # Configuration SSL
    ssl_verify = not args.no_ssl_verify
    
    # Test 1: Authentification
    auth_ok = test_gitlab_auth(args.url, token, ssl_verify)
    
    if not auth_ok:
        print("\n" + "=" * 70)
        print("❌ Le diagnostic a échoué à l'étape d'authentification")
        print("=" * 70)
        sys.exit(1)
    
    # Test 2: Accès au projet (si spécifié)
    if args.project:
        project_ok = test_project_access(args.url, token, args.project, ssl_verify)
        
        if not project_ok:
            print("\n" + "=" * 70)
            print("❌ Le diagnostic a échoué à l'étape d'accès au projet")
            print("=" * 70)
            sys.exit(1)
        
        # Test 3: Accès à la MR (si spécifiée)
        if args.mr:
            mr_ok = test_mr_access(args.url, token, args.project, args.mr, ssl_verify)
            
            if not mr_ok:
                print("\n" + "=" * 70)
                print("❌ Le diagnostic a échoué à l'étape d'accès à la MR")
                print("=" * 70)
                sys.exit(1)
    
    # Succès
    print("\n" + "=" * 70)
    print("✅ Tous les tests ont réussi !")
    print("=" * 70)
    print("\n💡 Votre token est valide et fonctionne correctement.")
    print("   Vous pouvez maintenant utiliser git-ia-mr sans problème.\n")


if __name__ == "__main__":
    main()
