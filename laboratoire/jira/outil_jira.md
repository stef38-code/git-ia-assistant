# Scénario d'intégration JIRA avec IA pour workflows Git

## 📋 Vue d'ensemble

Ce scénario décrit une **intégration complète entre Git, JIRA et l'IA** pour automatiser et enrichir les workflows de développement. L'objectif est de réduire drastiquement le temps passé sur l'administration JIRA et d'améliorer la traçabilité entre le code et les tickets.

## 🎯 Objectifs principaux

1. **Synchronisation automatique Git ↔ JIRA**
   - Lien automatique commits → tickets
   - Transitions de statut intelligentes
   - Commentaires automatiques sur les tickets

2. **Gestion de la dette technique**
   - Transformation des TODOs en tickets JIRA
   - Descriptions enrichies par l'IA
   - Traçabilité complète

3. **Analyse de sprint avec IA**
   - Rapports automatisés
   - Insights et recommandations
   - Détection des risques

4. **Amélioration de la qualité**
   - Descriptions de tickets enrichies
   - Critères d'acceptation générés
   - Estimations intelligentes

## 🚀 Fonctionnalités proposées

### 1. Commit avec synchronisation JIRA
**Commande** : `git-ia-commit-jira`

Workflow complet décrit dans → [workflow_commit_sync.md](./workflow_commit_sync.md)

**En résumé** :
- Détecte le ticket JIRA depuis la branche (`feature/PROJ-123`)
- Génère le message de commit avec IA
- Ajoute un commentaire sur le ticket JIRA
- Transite automatiquement le ticket
- Push vers Git

### 2. Création de tickets depuis les TODOs
**Commande** : `git-ia-jira --scan-todos`

Workflow complet décrit dans → [workflow_todos_tickets.md](./workflow_todos_tickets.md)

**En résumé** :
- Scanne le code pour détecter TODO/FIXME/HACK
- Génère des descriptions enrichies via IA
- Crée automatiquement les tickets JIRA
- Remplace les TODOs par des références JIRA

### 3. Rapport de sprint avec analyse IA
**Commande** : `git-ia-jira --sprint-report`

Workflow complet décrit dans → [workflow_sprint_report.md](./workflow_sprint_report.md)

**En résumé** :
- Récupère les tickets du sprint actif
- Analyse l'activité Git liée
- Génère des insights via IA
- Produit un rapport Markdown complet

### 4. Transition intelligente des tickets
**Commande** : `git-ia-jira --auto-transition`

Détecte automatiquement les mots-clés dans les commits et transite les tickets en conséquence.

### 5. Enrichissement de descriptions avec IA
**Commande** : `git-ia-jira PROJ-123 --enrich-description`

Analyse le contexte technique et génère une description enrichie pour le ticket.

## 📚 Organisation des fichiers

Ce scénario est organisé en plusieurs fichiers :

- **[outil_jira.md](./outil_jira.md)** (ce fichier) - Vue d'ensemble et index
- **[workflow_commit_sync.md](./workflow_commit_sync.md)** - Détails du commit avec synchronisation JIRA
- **[workflow_todos_tickets.md](./workflow_todos_tickets.md)** - Création de tickets depuis les TODOs
- **[workflow_sprint_report.md](./workflow_sprint_report.md)** - Rapports de sprint avec IA
- **[implementation_guide.md](./implementation_guide.md)** - Guide d'implémentation technique
- **[api_reference.md](./api_reference.md)** - Référence des APIs JIRA utilisées

## 🔐 Configuration requise

**Variables d'environnement** :
```bash
export JIRA_URL="https://votre-domaine.atlassian.net"
export JIRA_TOKEN="votre_api_token"
export JIRA_EMAIL="votre.email@example.com"
export JIRA_PROJECT="MYPROJECT"
export JIRA_BOARD_ID="123"  # optionnel
```

**Génération du token JIRA** :
1. Se connecter à https://id.atlassian.com/manage-profile/security/api-tokens
2. Créer un nouveau token avec le nom "git-ia-assistant"
3. Copier le token et le stocker dans la variable d'environnement

**Note de sécurité** : Les tokens ne doivent JAMAIS être committés dans Git. Toujours utiliser des variables d'environnement.

## 🎨 Commandes CLI complètes

```bash
# Commit avec synchronisation JIRA automatique
git-ia-commit-jira

# Scanner les TODOs et créer des tickets
git-ia-jira --scan-todos
git-ia-jira --scan-todos --types TODO,FIXME

# Enrichir la description d'un ticket avec IA
git-ia-jira PROJ-123 --enrich-description

# Générer un rapport de sprint
git-ia-jira --sprint-report
git-ia-jira --sprint-report --sprint-id 456

# Transition automatique d'un ticket
git-ia-jira PROJ-123 --transition "In Progress"

# Lister mes tickets en cours
git-ia-jira --my-issues

# Recherche personnalisée avec JQL
git-ia-jira --search "project = MYPROJECT AND status = \"To Do\""

# Mode dry-run (simulation)
git-ia-jira --scan-todos --dry-run
```

## ✅ Bénéfices attendus

### Pour les développeurs
- ⏱️ **Gain de temps** : Pas de saisie manuelle dans JIRA
- 🎯 **Focus sur le code** : Synchronisation automatique
- 📝 **Traçabilité** : Lien automatique code ↔ tickets
- 🧹 **Dette technique maîtrisée** : TODOs transformés en tickets

### Pour l'équipe
- 📊 **Visibilité** : Rapports de sprint avec insights IA
- 🔍 **Qualité** : Descriptions enrichies et critères d'acceptation
- ⚡ **Vélocité** : Analyse des performances et suggestions
- 🎯 **Priorisation** : Détection des risques et recommandations

### Pour le projet
- 📈 **Métriques fiables** : Activité Git liée aux tickets
- 🔄 **Workflow fluide** : Transitions automatiques
- 💡 **Amélioration continue** : Insights IA sur les sprints
- 🛡️ **Sécurité** : Credentials protégés par variables d'environnement

## 🚀 Plan de développement

### Phase 1 : Client JIRA basique ✅
- Connexion à l'API JIRA
- Récupération de tickets
- Ajout de commentaires
- Transitions de base

### Phase 2 : Synchronisation Git ↔ JIRA 🔄
- Détection du ticket depuis la branche
- Commentaire automatique au commit
- Transition automatique des tickets
- Hooks Git (pre-commit, post-commit, post-push)

### Phase 3 : Scan et création de tickets 📝
- Scanner les TODOs dans le code
- Enrichissement avec IA
- Création automatique de tickets
- Remplacement des TODOs par références JIRA

### Phase 4 : Rapports et analyse 📊
- Génération de rapports de sprint
- Analyse IA des métriques
- Export en différents formats (Markdown, JSON, HTML)
- Dashboard interactif (optionnel)

### Phase 5 : Fonctionnalités avancées 🚀
- Workflows personnalisés
- Règles de transition intelligentes
- Intégration avec `git-ia-review`
- Notifications Slack/Teams

## 📖 Documentation

### Pour commencer
1. Lire la [vue d'ensemble](./outil_jira.md) (ce fichier)
2. Consulter le [guide d'implémentation](./implementation_guide.md)
3. Explorer les [workflows détaillés](./workflow_commit_sync.md)

### Référence
- [API JIRA utilisées](./api_reference.md)
- [Configuration et sécurité](./implementation_guide.md#securite)
- [Exemples de prompts IA](./implementation_guide.md#prompts-ia)

## 🎯 Statut

**Statut actuel** : 📝 Scénario documenté, prêt pour implémentation

**Prochaine étape** : Implémenter le client JIRA basique (Phase 1)

---

**Note** : Ce scénario est conçu pour être modulaire. Chaque fonctionnalité peut être développée et déployée indépendamment.
