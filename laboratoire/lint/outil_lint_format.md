# 🎨 Lint & Format Intelligent avec IA

> **Commande** : `git-ia-lint`  
> **Statut** : 📝 En développement  
> **Priorité** : 🔴 Haute (Quick Win)  
> **Effort estimé** : 40 heures

---

## 📋 Vue d'ensemble

### Problème résolu

Les développ

eurs perdent un temps considérable à :
- Corriger manuellement les violations de linting signalées en review
- Comprendre *pourquoi* certaines règles existent
- Appliquer différents formatters selon les langages (black, prettier, spotless, etc.)
- Gérer les aller-retours dans les MR/PR pour des problèmes de style

**Impact** : 10-15 minutes perdues par jour/développeur pour des corrections de style.

### Solution proposée

`git-ia-lint` est un outil intelligent qui :
1. **Détecte automatiquement** le framework de linting du projet
2. **Analyse** les violations avec explication IA de chaque règle
3. **Corrige automatiquement** les problèmes de formatage
4. **S'intègre** avec git-ia-commit (pre-hook), git-ia-review, CI/CD

---

## 🎯 Fonctionnalités principales

### 1. Détection automatique du framework

```bash
# Auto-détecte le framework selon les fichiers de config
git-ia-lint                    # Analyse tout le projet
git-ia-lint src/UserService.java  # Fichier spécifique
```

**Fichiers de configuration détectés** :
- **Python** : `.pylintrc`, `pyproject.toml`, `setup.cfg`, `.flake8`
- **Java** : `checkstyle.xml`, `spotless.gradle`, `pom.xml` (maven-checkstyle)
- **JavaScript/TypeScript** : `eslint.config.js`, `.eslintrc.json`, `.prettierrc`
- **Shell** : `.shellcheckrc`

### 2. Analyse avec explications IA

```bash
# Mode verbeux : explique chaque violation
git-ia-lint --explain
```

**Exemple de sortie** :
```
❌ src/utils.py:45:1 - C0114 (missing-module-docstring)
   💡 Explication IA :
      Cette règle exige une docstring au début de chaque module Python.
      Elle améliore la documentation et aide les développeurs à comprendre
      rapidement l'objectif du fichier. Recommandation PEP 257.

   📝 Suggestion :
      """Module utilitaire pour la gestion des dates et timestamps."""
```

### 3. Correction automatique

```bash
# Corrige toutes les violations auto-fixables
git-ia-lint --apply

# Corrige + crée un commit
git-ia-lint --apply --commit

# Mode interactif
git-ia-lint --apply --interactive
```

---

## 🛠️ Frameworks supportés

### Python
- **Linters** : pylint, flake8, mypy, bandit
- **Formatters** : black, isort, autopep8

### Java
- **Linters** : checkstyle, spotbugs, PMD
- **Formatters** : spotless, google-java-format

### JavaScript/TypeScript
- **Linters** : eslint, tslint
- **Formatters** : prettier

### Shell
- **Linters** : shellcheck
- **Formatters** : shfmt

---

## 🔗 Intégrations

### Pre-commit Hook
```bash
# Installation automatique
git-ia-lint --install-hook

# Le hook applique automatiquement les corrections avant commit
```

### git-ia-commit
```bash
# Lance automatiquement git-ia-lint avant génération du message
git-ia-commit
```

### git-ia-review
```bash
# Inclut les violations de linting dans la review
git-ia-review fichier.py
```

### CI/CD
```bash
# Mode check pour CI/CD (exit 1 si violations)
git-ia-lint --check --format gitlab-codequality
```

---

## 📊 Formats de sortie

- **text** : Affichage console (défaut)
- **json** : Export JSON structuré
- **gitlab-codequality** : Format GitLab Code Quality
- **github** : Annotations GitHub Actions

---

## 🎓 Exemple complet

```bash
# 1. Analyse du code
git-ia-lint

# Sortie :
# 🎨 Analyse de linting - 5 fichiers
# ❌ src/utils.py (3 violations)
#    Line 45: C0114 missing-module-docstring
#    Line 78: C0301 line-too-long (125/120)
#    Line 92: W0611 unused-import 'os'

# 2. Correction automatique
git-ia-lint --apply

# Sortie :
# 🔧 Application des corrections...
# ✅ black appliqué (3 fichiers reformatés)
# ✅ isort appliqué (imports triés)
# ❌ 2 violations non auto-fixables restantes

# 3. Explications pour violations restantes
git-ia-lint --explain src/utils.py

# 4. Commit avec hook pré-installé
git-ia-commit
```

---

## 🚀 Roadmap

### Phase 1 - MVP (2 semaines)
- Support Python (pylint, black, isort)
- Mode `--apply` et `--check`
- CLI basique

### Phase 2 - Multi-langage (3 semaines)
- Support Java (checkstyle, spotless)
- Support TypeScript (eslint, prettier)
- Détection automatique

### Phase 3 - Intégrations (2 semaines)
- Pre-commit hook
- git-ia-commit / git-ia-review
- Formats GitLab/GitHub

### Phase 4 - IA (3 semaines)
- Explications IA des violations
- Suggestions de correction
- Mode interactif

---

**Valeur ajoutée** :
- ⏱️ Gain : 10-15 min/jour par développeur
- 📈 Qualité : respect automatique des conventions
- 🎓 Pédagogie : comprendre les règles de linting

**Date de dernière mise à jour** : Mars 2026
