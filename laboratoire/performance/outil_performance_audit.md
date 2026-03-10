# ⚡ Performance Audit + Suggestions

> **Commande** : `git-ia-perf`  
> **Statut** : 📝 Idée à explorer  
> **Priorité** : 🟣 Basse  
> **Effort estimé** : 50 heures

---

## 📋 Vue d'ensemble

`git-ia-perf` analyse les performances du code et suggère des optimisations.

---

## 🎯 Fonctionnalités principales

### 1. Analyse de performance
```bash
# Analyse un fichier
git-ia-perf analyze --file src/HeavyAlgo.java --profile time,memory

# Analyse complète du projet
git-ia-perf analyze --all --threshold 500ms
```

**Métriques collectées** :
- **Temps d'exécution** : fonctions > seuil
- **Utilisation mémoire** : détection de fuites
- **Complexité algorithmique** : O(n²), O(n log n), etc.
- **Requêtes SQL** : N+1 queries

**Exemple de sortie** :
```
⚡ Analyse de performance : src/UserService.java

Fonctions lentes (> 500ms) :
┌────────────────────────┬──────────┬────────────┬─────────────┐
│ Fonction               │ Temps    │ Complexité │ Suggestions │
├────────────────────────┼──────────┼────────────┼─────────────┤
│ findAllUsers()         │ 1250ms   │ O(n²)      │ 3           │
│ calculateTotalRevenue()│ 850ms    │ O(n)       │ 2           │
└────────────────────────┴──────────┴────────────┴─────────────┘

💡 IA suggère pour findAllUsers() :
1. Utiliser pagination (LIMIT/OFFSET)
2. Ajouter index sur user.created_at
3. Charger relations en lazy loading
```

---

### 2. Suggestions d'optimisation
```bash
# Affiche suggestions IA
git-ia-perf suggest --file src/UserService.java --optimize

# Applique les optimisations automatiquement
git-ia-perf optimize --file src/UserService.java --auto-apply
```

**Types d'optimisations** :
- **Algorithmes** : remplacement par version plus rapide
- **Cache** : ajout de mise en cache
- **Requêtes** : optimisation SQL (indexes, joins)
- **Mémoire** : réduction de l'empreinte mémoire

---

### 3. Profiling intégré
```bash
# Profile une fonction spécifique
git-ia-perf profile --function calculateTotalRevenue --iterations 1000

# Résultat :
# Average : 850ms
# Min : 720ms
# Max : 1200ms
# P95 : 980ms
#
# Hotspots détectés :
# - Line 45 : boucle foreach (600ms / 70%)
# - Line 78 : query SQL (200ms / 24%)
```

---

### 4. Détection de patterns anti-performance
```bash
# Scan du projet pour patterns lents
git-ia-perf scan --anti-patterns

# Détecte :
# - N+1 queries (ORM)
# - Boucles imbriquées inutiles
# - String concatenation en boucle (Java)
# - Utilisation de ++ au lieu de += (Python)
```

---

## 🔗 Intégrations

### 1. git-ia-review
```bash
# Inclut analyse de performance dans la review
git-ia-review --include-perf fichier.java
```

### 2. CI/CD
```bash
# Bloque si régression de performance
git-ia-perf check --baseline perf-baseline.json --fail-if-slower 10%
```

---

## 📊 Rapport de performance

```bash
# Génère rapport HTML
git-ia-perf report --output perf-report.html

# Compare 2 versions
git-ia-perf compare --before v1.0 --after v2.0 --output diff-report.html
```

---

## 🎓 Exemples d'utilisation

### Scénario 1 : Optimisation d'une API lente

```bash
# 1. Détection du problème
git-ia-perf analyze --file src/UserService.java

# ⚠️  findAllUsers() : 1250ms (seuil : 500ms)

# 2. Suggestions IA
git-ia-perf suggest --function findAllUsers

# 💡 Suggestion 1 : Ajouter pagination
# 💡 Suggestion 2 : Index sur user.created_at
# 💡 Suggestion 3 : Cache Redis

# 3. Application d'une suggestion
git-ia-perf optimize --function findAllUsers --suggestion 1

# ✅ Pagination ajoutée
# ✅ Tests générés

# 4. Vérification
git-ia-perf profile --function findAllUsers
# ✅ Nouveau temps : 120ms (-90%)
```

---

## 🚀 Roadmap

### Phase 1 - MVP (2 semaines)
- Profiling basique (temps d'exécution)
- Détection de patterns lents simples
- CLI basique

### Phase 2 - Optimisations IA (3 semaines)
- Suggestions IA d'optimisation
- Application automatique
- Support Java/Python/TypeScript

### Phase 3 - Intégrations (1 semaine)
- git-ia-review
- CI/CD checks
- Rapports HTML

---

**Valeur ajoutée** :
- ⚡ Performances améliorées automatiquement
- 🎯 Détection proactive des goulots d'étranglement
- ⏱️ Gain : 1-2 jours pour optimisations manuelles

**Date de dernière mise à jour** : Mars 2026
