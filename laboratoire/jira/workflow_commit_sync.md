# Workflow : Commit avec synchronisation JIRA

## 📋 Vue d'ensemble

Ce workflow permet de **committer du code tout en synchronisant automatiquement JIRA**, éliminant le besoin de mises à jour manuelles des tickets.

**Commande** : `git-ia-commit-jira`

## 🎯 Objectif

Automatiser complètement la synchronisation entre les commits Git et les tickets JIRA pour :
- Lier automatiquement chaque commit à un ticket
- Transitionner le ticket selon l'état du développement
- Maintenir JIRA à jour sans effort manuel
- Améliorer la traçabilité code ↔ tickets

## 🔄 Workflow détaillé

### Étape 1 : Détection du ticket JIRA

Le script analyse le nom de la branche Git pour extraire la référence JIRA.

**Exemples de noms de branches supportés** :
```
feature/PROJ-123-ajouter-api          → PROJ-123
bugfix/MYAPP-456-corriger-login       → MYAPP-456
hotfix/ABC-789                        → ABC-789
chore/XYZ-111-maj-dependances         → XYZ-111
```

**Pattern de détection** : `[A-Z][A-Z0-9]+-\d+`

### Étape 2 : Génération du message de commit

Utilise l'IA (comme `git-ia-commit` classique) pour générer un message conforme à Conventional Commits.

**Exemple de message généré** :
```
feat(api): ajouter endpoint de création d'utilisateurs

- Implémente POST /api/users avec validation
- Ajoute tests unitaires pour la création
- Documente l'endpoint dans Swagger
```

### Étape 3 : Commit Git local

Le commit est créé localement avec le message généré.

```bash
git commit -m "feat(api): ajouter endpoint de création d'utilisateurs

- Implémente POST /api/users avec validation
- Ajoute tests unitaires pour la création
- Documente l'endpoint dans Swagger"
```

### Étape 4 : Récupération des infos du ticket JIRA

Le script interroge l'API JIRA pour obtenir les informations du ticket :
- Titre (summary)
- Statut actuel
- Assigné
- Priorité

**Endpoint utilisé** : `GET /rest/api/3/issue/PROJ-123`

### Étape 5 : Ajout d'un commentaire sur le ticket

Un commentaire est automatiquement ajouté au ticket JIRA avec :
- Le hash du commit (SHA court)
- Le message de commit complet
- Un lien vers le commit (si configuré)

**Format du commentaire** :
```
🔧 Commit effectué : abc1234

feat(api): ajouter endpoint de création d'utilisateurs

- Implémente POST /api/users avec validation
- Ajoute tests unitaires pour la création
- Documente l'endpoint dans Swagger

Branche : feature/PROJ-123-ajouter-api
Auteur : John Doe
Date : 2026-03-06 15:30:00
```

**Endpoint utilisé** : `POST /rest/api/3/issue/PROJ-123/comment`

### Étape 6 : Transition automatique du ticket

Le ticket est automatiquement transitionné selon des règles configurables.

**Règles par défaut** :
- Si le ticket est "To Do" → Passe à "In Progress"
- Si le ticket est déjà "In Progress" → Reste "In Progress"
- Si le ticket est "Done" → Aucune transition (log warning)

**Transitions personnalisables** via configuration :
```yaml
# .git-ia-jira.yml
transitions:
  first_commit: "In Progress"   # ID: 11
  after_push: "In Review"        # ID: 21
  on_close: "Done"               # ID: 31
```

**Endpoint utilisé** : `POST /rest/api/3/issue/PROJ-123/transitions`

### Étape 7 : Push Git

Le commit est poussé vers le dépôt distant.

```bash
git push origin feature/PROJ-123-ajouter-api
```

**Note** : Si un hook `post-push` est configuré, il peut déclencher une transition supplémentaire (ex: "In Review").

## 💡 Exemples d'usage

### Exemple 1 : Commit simple

```bash
# Branche : feature/PROJ-123-ajouter-api
git add src/api/users.py
git-ia-commit-jira

# Résultat :
# ✅ Message généré par l'IA
# ✅ Commit créé : abc1234
# ✅ Commentaire ajouté sur PROJ-123
# ✅ Ticket PROJ-123 : "To Do" → "In Progress"
# ✅ Push effectué
```

### Exemple 2 : Commit avec plusieurs fichiers

```bash
# Branche : bugfix/MYAPP-456-corriger-login
git add src/auth/*.py tests/test_auth.py
git-ia-commit-jira

# Message généré :
# fix(auth): corriger la validation du token JWT
# 
# - Corrige l'expiration prématurée des tokens
# - Ajoute tests pour les cas limites
# - Met à jour la documentation
```

### Exemple 3 : Mode dry-run (simulation)

```bash
git-ia-commit-jira --dry-run

# Affiche :
# 📋 Ticket détecté : PROJ-123
# 📝 Message qui serait généré : ...
# 💬 Commentaire qui serait ajouté : ...
# 🔄 Transition qui serait effectuée : "To Do" → "In Progress"
# ⚠️  Mode dry-run : aucune action réelle
```

### Exemple 4 : Forcer une transition spécifique

```bash
git-ia-commit-jira --transition "In Review"

# Force la transition vers "In Review"
# même si les règles par défaut diraient autre chose
```

## 🎨 Options CLI

```bash
# Usage complet
git-ia-commit-jira [OPTIONS]

Options:
  -h, --help              Afficher l'aide
  --dry-run               Simuler sans exécuter
  --ia <provider>         Fournisseur IA (copilot, gemini, ollama)
  --transition <status>   Forcer une transition spécifique
  --no-push               Commit sans push
  --no-comment            Ne pas ajouter de commentaire JIRA
  --no-transition         Ne pas transitionner le ticket
```

### Exemples avec options

```bash
# Commit avec Gemini et sans push
git-ia-commit-jira --ia gemini --no-push

# Commit sans transitionner le ticket
git-ia-commit-jira --no-transition

# Simulation complète
git-ia-commit-jira --dry-run --ia ollama
```

## 🔧 Configuration avancée

### Fichier de configuration (optionnel)

Créer `.git-ia-jira.yml` à la racine du projet :

```yaml
# Configuration JIRA
jira:
  url: "https://votre-domaine.atlassian.net"
  project: "MYPROJECT"

# Règles de transition
transitions:
  on_first_commit: "In Progress"      # ID ou nom
  on_push: "In Review"
  on_pr_merge: "Done"
  
  # Conditions personnalisées
  rules:
    - if: "commit_message contains 'WIP'"
      then: null  # Aucune transition
    
    - if: "commit_message contains 'Closes'"
      then: "Done"

# Format du commentaire
comment:
  template: |
    🔧 Commit {commit_sha}
    
    {commit_message}
    
    📂 Fichiers modifiés : {files_count}
    👤 Auteur : {author}
  
  include_diff: false  # Ne pas inclure le diff dans le commentaire

# Push automatique
auto_push: true

# Notification
notifications:
  slack_webhook: "https://hooks.slack.com/services/XXX"
  on_transition: true
```

### Variables d'environnement

Toujours prioritaires sur le fichier de configuration :

```bash
export JIRA_URL="https://votre-domaine.atlassian.net"
export JIRA_TOKEN="votre_token"
export JIRA_EMAIL="votre.email@example.com"
export JIRA_PROJECT="MYPROJECT"
```

## 🔄 Intégration avec les hooks Git

### Hook post-commit (automatique)

Créer `.git/hooks/post-commit` :

```bash
#!/bin/bash
# Hook exécuté après chaque commit

# Lancer git-ia-commit-jira en mode silent
git-ia-commit-jira --auto-sync --quiet

exit 0
```

**Avantages** :
- Synchronisation automatique après chaque `git commit`
- Pas besoin de se rappeler la commande
- Workflow fluide

**Inconvénients** :
- Requiert une connexion internet
- Ajoute ~2-3 secondes au commit

### Hook post-push (transition finale)

Créer `.git/hooks/post-push` :

```bash
#!/bin/bash
# Hook exécuté après git push

# Transitionner le ticket vers "In Review"
git-ia-jira --auto-transition --status "In Review" --quiet

exit 0
```

## 📊 Suivi et logs

### Logs détaillés

Activer les logs verbeux :

```bash
git-ia-commit-jira --verbose

# Affiche :
# 🔍 Détection du ticket...
# ✅ Ticket trouvé : PROJ-123
# 📝 Génération du message avec copilot...
# ✅ Message généré (142 caractères)
# 💾 Création du commit...
# ✅ Commit créé : abc1234
# 🌐 Connexion à JIRA...
# ✅ Connecté à https://votre-domaine.atlassian.net
# 💬 Ajout du commentaire...
# ✅ Commentaire ajouté (ID: 12345)
# 🔄 Transition du ticket...
# ✅ Ticket transitionné : "To Do" → "In Progress"
# 📤 Push vers origin...
# ✅ Push effectué
```

### Logs JSON (pour scripting)

```bash
git-ia-commit-jira --json > commit_result.json

# Contenu de commit_result.json :
{
  "success": true,
  "ticket_key": "PROJ-123",
  "commit_sha": "abc1234567890",
  "commit_message": "feat(api): ...",
  "jira_comment_id": "12345",
  "transition": {
    "from": "To Do",
    "to": "In Progress"
  },
  "pushed": true
}
```

## ⚠️ Gestion des erreurs

### Erreur : Branche sans ticket JIRA

```bash
# Sur la branche "main"
git-ia-commit-jira

# Erreur :
# ❌ Aucun ticket JIRA détecté dans le nom de la branche
# 💡 Utilisez un nom de branche contenant une référence JIRA
#    Exemples : feature/PROJ-123, bugfix/APP-456
```

**Solution** : Utiliser `git-ia-commit` classique ou renommer la branche.

### Erreur : Ticket inexistant

```bash
# Branche : feature/PROJ-999-inexistant
git-ia-commit-jira

# Erreur :
# ❌ Le ticket PROJ-999 n'existe pas dans JIRA
# 🔍 Vérifiez que le ticket existe et que vous avez les permissions
```

**Solution** : Corriger la référence du ticket dans le nom de la branche.

### Erreur : Transition impossible

```bash
git-ia-commit-jira

# Avertissement :
# ⚠️  Impossible de transitionner PROJ-123 : "Done" → "In Progress"
# ℹ️  Le ticket est déjà terminé
# ✅ Commit et commentaire créés malgré tout
```

**Comportement** : Le commit et le commentaire sont créés, seule la transition échoue.

### Erreur : Pas de connexion internet

```bash
git-ia-commit-jira

# Erreur :
# ❌ Impossible de se connecter à JIRA
# 💡 Vérifiez votre connexion internet
# 💾 Le commit local a été créé
# ⚠️  Utilisez --retry pour réessayer la synchronisation JIRA
```

**Solution** : Réessayer avec `git-ia-commit-jira --retry-last`

## 🔒 Sécurité

### Protection des credentials

- ✅ Les tokens JIRA sont stockés dans des variables d'environnement
- ✅ Les tokens ne sont JAMAIS loggés en clair
- ✅ Les requêtes utilisent HTTPS obligatoirement
- ✅ Les tokens ont une durée de vie limitée (configurable dans JIRA)

### Validation des données

- Validation du format de la clé JIRA avant envoi
- Sanitisation des commentaires (limite de taille, caractères spéciaux)
- Vérification des permissions avant transition

## 📈 Métriques et analytics

### Statistiques de synchronisation

```bash
git-ia-jira --stats

# Affiche :
# 📊 Statistiques de synchronisation JIRA
# 
# Période : 7 derniers jours
# 
# ✅ Commits synchronisés : 42
# 💬 Commentaires ajoutés : 42
# 🔄 Transitions effectuées : 38
# ❌ Échecs : 2 (4.8%)
# 
# Tickets les plus actifs :
#   1. PROJ-123 (8 commits)
#   2. PROJ-124 (5 commits)
#   3. PROJ-125 (4 commits)
```

## 🎯 Bonnes pratiques

### 1. Nommer correctement les branches

```bash
# ✅ BON
feature/PROJ-123-ajouter-authentification
bugfix/APP-456-corriger-validation
hotfix/SERV-789-patch-securite

# ❌ MAUVAIS
ma-feature
correction-bug
ajout-fonctionnalite
```

### 2. Commits atomiques

Un commit = une fonctionnalité/correction = un ticket JIRA

### 3. Messages de commit clairs

Laisser l'IA générer des messages conformes à Conventional Commits.

### 4. Vérifier avant de pousser

Utiliser `--dry-run` pour simuler avant la synchronisation réelle.

### 5. Configurer les transitions

Adapter les transitions selon le workflow de l'équipe.

## 🚀 Prochaines évolutions

- [ ] Support des sous-tâches JIRA
- [ ] Gestion des sprints (lien automatique au sprint actif)
- [ ] Notification Slack/Teams après transition
- [ ] Dashboard web pour visualiser les synchronisations
- [ ] Support multi-tickets (pour les commits touchant plusieurs tickets)

## 📚 Voir aussi

- [Création de tickets depuis TODOs](./workflow_todos_tickets.md)
- [Rapports de sprint](./workflow_sprint_report.md)
- [API JIRA utilisées](./api_reference.md)
- [Guide d'implémentation](./implementation_guide.md)
