# Dépannage GitLab - Erreur 401 Unauthorized

Guide de résolution des problèmes d'authentification GitLab pour la commande `git-ia-mr`.

## 🔍 Symptôme

```
[ERREUR] Le token GitLab est invalide ou n'a pas les droits nécessaires
gitlab.exceptions.GitlabAuthenticationError: 401: 401 Unauthorized
```

## ✅ Solution rapide

### 1. Exporter le token

Dans votre terminal (celui où vous exécutez le script) :

```bash
export GIT_TOKEN='votre_token_gitlab'
```

⚠️ **Important** : Le token doit être exporté dans le **même terminal** où vous lancez `git-ia-mr`.

### 2. Vérifier que le token est défini

```bash
echo $GIT_TOKEN
```

Doit afficher votre token complet (sans espaces ni caractères parasites).

### 3. Utiliser le script de diagnostic

```bash
# Test simple de connexion
python src/git_ia_assistant/debug/mr_cli/diagnose_gitlab_auth.py \
    -u https://gitlab.com

# Test complet avec projet et MR
python src/git_ia_assistant/debug/mr_cli/diagnose_gitlab_auth.py \
    -u https://gitlab.com \
    -p groupe/projet \
    -m 123

# Pour un serveur avec certificat auto-signé
python src/git_ia_assistant/debug/mr_cli/diagnose_gitlab_auth.py \
    -u https://gitlab.example.com \
    --no-ssl-verify \
    -p groupe/projet \
    -m 123
```

Ce script teste :
- ✅ Connexion à GitLab
- ✅ Authentification avec le token
- ✅ Accès au projet
- ✅ Accès à la MR

## 🔧 Vérifications détaillées

### Vérifier les scopes du token

Sur GitLab (Settings → Access Tokens), vérifiez que votre token a **au minimum** :

- ✅ `read_api` ← **OBLIGATOIRE**
- ✅ `read_repository` ← Recommandé

### Vérifier que le token n'est pas expiré

Les tokens GitLab ont une date d'expiration. Si votre token est expiré, créez-en un nouveau.

### Tester manuellement avec curl

```bash
curl -k -H "PRIVATE-TOKEN: $GIT_TOKEN" \
     "https://gitlab.example.com/api/v4/user"
```

**Résultat attendu** : Vos informations utilisateur en JSON

```json
{
  "id": 123,
  "username": "votre_username",
  "name": "Votre Nom",
  ...
}
```

**Si erreur 401** : Le token est invalide ou expiré → créez un nouveau token

## 🛠️ Problèmes courants

| Problème | Solution |
|----------|----------|
| Token avec espaces | Vérifiez : `echo "$GIT_TOKEN" \| wc -c` |
| Token dans un autre terminal | Exportez dans **le même terminal** |
| Token expiré | Créez un nouveau token sur GitLab |
| Mauvais scopes | Créez un nouveau token avec `read_api` |
| Projet privé | Vérifiez que vous avez accès au projet |
| Certificat SSL auto-signé | Utilisez `--no-ssl-verify` |

## 💡 Configuration permanente

Pour ne pas avoir à exporter le token à chaque fois :

### Option 1 : Dans ~/.bashrc

```bash
echo "export GIT_TOKEN='votre_token'" >> ~/.bashrc
source ~/.bashrc
```

### Option 2 : Fichier .env dédié

```bash
echo "export GIT_TOKEN='votre_token'" > ~/.env-git-ia
echo "source ~/.env-git-ia" >> ~/.bashrc
source ~/.bashrc
```

⚠️ **Sécurité** : Ne committez jamais votre token dans Git !

## 📚 Utilisation du script de diagnostic

### Syntaxe

```bash
python src/git_ia_assistant/debug/mr_cli/diagnose_gitlab_auth.py [OPTIONS]
```

### Options

| Option | Description |
|--------|-------------|
| `-u, --url URL` | URL de l'instance GitLab (obligatoire) |
| `-p, --project PATH` | Chemin du projet (ex: groupe/projet) |
| `-m, --mr NUMBER` | Numéro de la Merge Request |
| `-t, --token TOKEN` | Token GitLab (sinon utilise GIT_TOKEN) |
| `--no-ssl-verify` | Désactiver la vérification SSL |
| `-h, --help` | Afficher l'aide |

### Exemples

```bash
# Test connexion simple
python src/git_ia_assistant/debug/mr_cli/diagnose_gitlab_auth.py \
    -u https://gitlab.com

# Test avec projet
python src/git_ia_assistant/debug/mr_cli/diagnose_gitlab_auth.py \
    -u https://gitlab.com \
    -p mygroup/myproject

# Test complet (connexion + projet + MR)
python src/git_ia_assistant/debug/mr_cli/diagnose_gitlab_auth.py \
    -u https://gitlab.com \
    -p mygroup/myproject \
    -m 456

# Serveur privé sans vérification SSL
python src/git_ia_assistant/debug/mr_cli/diagnose_gitlab_auth.py \
    -u https://gitlab.example.com \
    --no-ssl-verify

# Token spécifique (au lieu de $GIT_TOKEN)
python src/git_ia_assistant/debug/mr_cli/diagnose_gitlab_auth.py \
    -u https://gitlab.com \
    -t glpat-xxxxxxxxxxxxxxxxxxxx
```

## 📞 Besoin d'aide ?

Si le problème persiste après avoir suivi ces étapes :

1. Exécutez le script de diagnostic avec vos paramètres
2. Vérifiez les logs complets
3. Testez manuellement avec `curl` (voir ci-dessus)
4. Vérifiez que vous avez bien accès au projet sur GitLab
5. Créez un nouveau token avec les bons scopes

## 🔐 Créer un nouveau token GitLab

1. Connectez-vous sur votre instance GitLab
2. Allez dans : **User Settings** (icône profil) → **Access Tokens**
3. Créez un nouveau token avec :
   - **Name** : `git-ia-assistant`
   - **Scopes** : 
     - ✅ `read_api` (obligatoire)
     - ✅ `read_repository` (recommandé)
   - **Expiration** : définissez selon vos besoins
4. Cliquez sur **Create personal access token**
5. **Copiez le token** (⚠️ il ne sera affiché qu'une seule fois !)
6. Exportez-le : `export GIT_TOKEN='votre_nouveau_token'`
