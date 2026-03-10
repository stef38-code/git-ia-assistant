# 📦 Gestion des Dépendances Intelligente

> **Commande** : `git-ia-deps`  
> **Statut** : 📝 En développement  
> **Priorité** : 🟢 Moyenne-Haute  
> **Effort estimé** : 50 heures

---

## 📋 Vue d'ensemble

### Problème résolu

Les développeurs doivent :
- Surveiller manuellement les vulnérabilités (CVE) dans les dépendances
- Upgrader les dépendances de manière sécurisée (SemVer)
- Nettoyer les dépendances inutilisées
- Créer des PR/MR pour chaque upgrade

**Impact** : 2-3 heures/mois par projet pour la veille de sécurité.

### Solution proposée

`git-ia-deps` gère automatiquement les dépendances avec :
1. **Audit de sécurité** : détection CVE + SBOM
2. **Upgrade sécurisé** : respect SemVer (patch, minor, major)
3. **Nettoyage** : détection dépendances inutilisées
4. **Automatisation** : création MR/PR automatique

---

## 🎯 Fonctionnalités principales

### 1. Audit de sécurité

```bash
# Audit complet (CVE + SBOM)
git-ia-deps audit

# Affiche uniquement les vulnérabilités
git-ia-deps audit --show-vulnerabilities

# Filtre par criticité
git-ia-deps audit --severity critical
git-ia-deps audit --severity high,critical
```

**Exemple de sortie** :
```
🔍 Audit de sécurité - 3 vulnérabilités détectées

┌──────────┬────────────┬──────────┬─────────────────────────┐
│ Severity │ Package    │ Version  │ CVE                     │
├──────────┼────────────┼──────────┼─────────────────────────┤
│ CRITICAL │ lodash     │ 4.17.15  │ CVE-2021-23337          │
│ HIGH     │ spring-web │ 5.2.3    │ CVE-2021-22096          │
│ MODERATE │ axios      │ 0.21.1   │ CVE-2021-3749           │
└──────────┴────────────┴──────────┴─────────────────────────┘

💡 Suggestion IA :
   - lodash : upgrade vers 4.17.21 (fix disponible)
      → Pas de breaking change
      → Safe pour upgrade automatique
   
   - spring-web : upgrade vers 5.3.9
      → Nécessite upgrade Spring Boot vers 2.5.x
      → Breaking changes possibles
      → Recommandé : upgrade manuel + tests
   
   - axios : upgrade vers 0.21.4
      → Patch uniquement
      → Safe pour upgrade automatique

Appliquer les corrections automatiques (lodash, axios) ? [y/n/c: créer MR] : c
```

---

### 2. Upgrade sécurisé

```bash
# Upgrade sûr (patch + minor uniquement)
git-ia-deps upgrade --safe

# Upgrade avec major (demande confirmation)
git-ia-deps upgrade --major --confirm

# Upgrade d'une dépendance spécifique
git-ia-deps upgrade --dep lodash --to 4.17.21

# Dry-run (affiche ce qui sera fait sans modifier)
git-ia-deps upgrade --safe --dry-run
```

**Respect de SemVer** :
- **Patch** (1.2.3 → 1.2.4) : Safe, auto-appliqué avec `--safe`
- **Minor** (1.2.3 → 1.3.0) : Safe, auto-appliqué avec `--safe`
- **Major** (1.2.3 → 2.0.0) : Breaking changes possibles, nécessite `--major --confirm`

**Exemple de sortie** :
```
🔄 Upgrade des dépendances (mode --safe)

Upgrades disponibles :
┌──────────────┬─────────┬─────────┬──────────┬────────┐
│ Package      │ Current │ Latest  │ Type     │ Action │
├──────────────┼─────────┼─────────┼──────────┼────────┤
│ lodash       │ 4.17.15 │ 4.17.21 │ PATCH    │ ✅ Auto│
│ axios        │ 0.21.1  │ 0.21.4  │ PATCH    │ ✅ Auto│
│ spring-boot  │ 2.3.4   │ 2.7.10  │ MINOR    │ ✅ Auto│
│ react        │ 17.0.2  │ 18.2.0  │ MAJOR    │ ⏭️ Skip│
└──────────────┴─────────┴─────────┴──────────┴────────┘

💡 IA analyse :
   - lodash : correctif de sécurité (CVE-2021-23337)
   - axios : correctif de sécurité (CVE-2021-3749)
   - spring-boot : 15 correctifs + nouvelles fonctionnalités
   - react : breaking changes (voir release notes)

Appliquer 3 upgrades (lodash, axios, spring-boot) ? [y/n] : y

✅ Upgrades appliqués :
   - package.json mis à jour
   - pom.xml mis à jour
   
Créer un commit ? [y/n] : y
✅ Commit créé : "chore(deps): upgrade lodash, axios, spring-boot"

Créer une MR ? [y/n] : y
✅ MR créée : !142 "chore(deps): upgrade dependencies (3 packages)"
   → https://gitlab.com/project/merge_requests/142
```

---

### 3. Nettoyage des dépendances

```bash
# Détecte dépendances inutilisées
git-ia-deps check --unused

# Détecte versions multiples (duplicates)
git-ia-deps check --duplicates

# Propose suppression interactive
git-ia-deps check --unused --remove-prompt
```

**Exemple de sortie** :
```
🧹 Analyse des dépendances inutilisées

Dépendances non utilisées détectées :
┌────────────────┬───────────┬─────────────────────────┐
│ Package        │ Version   │ Dernière utilisation    │
├────────────────┼───────────┼─────────────────────────┤
│ moment         │ 2.29.4    │ Aucune importation      │
│ underscore     │ 1.13.6    │ Remplacé par lodash     │
│ xml2js         │ 0.5.0     │ Aucune importation      │
└────────────────┴───────────┴─────────────────────────┘

💡 IA suggère :
   - moment : remplacé par date-fns dans le code
   - underscore : lodash fournit les mêmes fonctions
   - xml2js : aucun fichier n'importe ce package

Supprimer ces dépendances ? [y: oui, n: non, s: sélectionner] : s

Supprimer moment ? [y/n] : y ✅
Supprimer underscore ? [y/n] : y ✅
Supprimer xml2js ? [y/n] : n ⏭️

✅ 2 dépendances supprimées
📦 Taille package.json : 1.2 MB → 950 KB (-250 KB)

Créer un commit ? [y/n] : y
✅ Commit : "chore(deps): remove unused dependencies (moment, underscore)"
```

---

### 4. Création automatique de MR/PR

```bash
# Upgrade + création MR automatique
git-ia-deps upgrade --safe --create-mr

# Fix vulnérabilités + MR
git-ia-deps audit --fix-vulns --create-mr

# MR avec template personnalisé
git-ia-deps upgrade --safe --create-mr --template .gitlab/templates/dependency-upgrade.md
```

**Contenu de la MR générée** :
```markdown
## 📦 Upgrade de dépendances

### Résumé
- 3 packages upgradés (patch/minor)
- 2 vulnérabilités corrigées (CVE)
- 0 breaking change

### Packages modifiés

#### lodash : 4.17.15 → 4.17.21 (PATCH)
- **Raison** : Correctif de sécurité CVE-2021-23337
- **Breaking changes** : Aucun
- **Tests requis** : ✅ Automatiques suffisants

#### axios : 0.21.1 → 0.21.4 (PATCH)
- **Raison** : Correctif de sécurité CVE-2021-3749
- **Breaking changes** : Aucun
- **Tests requis** : ✅ Automatiques suffisants

#### spring-boot : 2.3.4 → 2.7.10 (MINOR)
- **Raison** : Correctifs + nouvelles fonctionnalités
- **Breaking changes** : Aucun
- **Tests requis** : ⚠️ Vérifier intégrations Spring

### Sécurité

🔒 **2 CVE corrigées** :
- CVE-2021-23337 (CRITICAL) - lodash prototype pollution
- CVE-2021-3749 (MODERATE) - axios SSRF vulnerability

### Checklist

- [x] Tests automatiques passent
- [x] Aucun breaking change
- [ ] Tests manuels requis (Spring Boot)
- [ ] Revue de code requise

### Commandes pour tester localement

```bash
# Installer les nouvelles dépendances
npm install  # ou mvn install

# Lancer les tests
npm test     # ou mvn test

# Vérifier l'application
npm run dev
```

---

**Généré automatiquement par `git-ia-deps`**
```

---

## 🛠️ Langages supportés

### Java (Maven / Gradle)

**Fichiers gérés** :
- `pom.xml` (Maven)
- `build.gradle` / `build.gradle.kts` (Gradle)

**Commandes utilisées** :
- `mvn versions:display-dependency-updates`
- `mvn dependency-check:check` (OWASP)
- `gradle dependencyUpdates`

**Exemple** :
```bash
git-ia-deps audit --framework java

# Utilise :
# - mvn dependency-check:check pour CVE
# - mvn versions:display-dependency-updates pour upgrades
```

---

### Node.js (npm / yarn / pnpm)

**Fichiers gérés** :
- `package.json`
- `package-lock.json` / `yarn.lock` / `pnpm-lock.yaml`

**Commandes utilisées** :
- `npm audit`
- `yarn audit`
- `npm outdated`

**Exemple** :
```bash
git-ia-deps audit --framework node

# Utilise :
# - npm audit pour CVE
# - npm outdated pour upgrades disponibles
```

---

### Python (pip / poetry)

**Fichiers gérés** :
- `requirements.txt`
- `pyproject.toml`
- `Pipfile`

**Commandes utilisées** :
- `pip-audit` (CVE scan)
- `safety check`
- `pip list --outdated`

**Exemple** :
```bash
git-ia-deps audit --framework python

# Utilise :
# - pip-audit pour CVE
# - pip list --outdated pour upgrades
```

---

## 🔗 Intégrations

### 1. git-ia-commit
```bash
# Upgrade + commit automatique
git-ia-deps upgrade --safe --commit
```

### 2. git-ia-changelog
```bash
# Enregistre les upgrades dans CHANGELOG.md
git-ia-deps upgrade --safe --update-changelog
```

### 3. SonarQube
```bash
# Synchronise avec alertes SonarQube
git-ia-deps sync-sonar --project my-app
```

### 4. JIRA
```bash
# Crée ticket JIRA pour vulnérabilités critiques
git-ia-deps audit --create-jira-tickets --severity critical

# Résultat :
# → Ticket créé : "SECURITY-123: Fix CVE-2021-23337 in lodash"
```

---

## 📊 Génération de SBOM

```bash
# Génère Software Bill of Materials
git-ia-deps report --sbom --format cyclonedx --output sbom.json

# Formats supportés :
# - cyclonedx (JSON/XML)
# - spdx (JSON/RDF)
# - custom (Markdown)
```

**Exemple de SBOM généré** :
```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.4",
  "version": 1,
  "components": [
    {
      "type": "library",
      "name": "lodash",
      "version": "4.17.21",
      "purl": "pkg:npm/lodash@4.17.21",
      "licenses": [{"license": {"id": "MIT"}}]
    }
  ]
}
```

---

## 🎓 Exemples d'utilisation

### Scénario 1 : Audit de sécurité mensuel

```bash
# 1. Audit complet
git-ia-deps audit --show-vulnerabilities

# 2. Fix automatique des vulnérabilités patchables
git-ia-deps audit --fix-vulns --safe

# 3. Création MR pour review
git-ia-deps audit --fix-vulns --create-mr --assignee @security-team

# 4. Rapport SBOM pour audit
git-ia-deps report --sbom --output sbom-$(date +%Y-%m).json
```

---

### Scénario 2 : CI/CD bloque si vulnérabilités critiques

```yaml
# .gitlab-ci.yml
security-audit:
  stage: security
  script:
    - pip install git-ia-assistant
    - git-ia-deps audit --severity critical --fail-if-found
  only:
    - merge_requests
  allow_failure: false
```

---

## 🚀 Roadmap

### Phase 1 - MVP (2 semaines)
- Support npm audit
- Commande `audit` et `upgrade --safe`
- Affichage console

### Phase 2 - Multi-langage (2 semaines)
- Support Maven/Gradle
- Support pip/poetry
- Détection automatique

### Phase 3 - Automatisation (1 semaine)
- Création MR/PR automatique
- Intégration git-ia-commit
- Templates personnalisés

### Phase 4 - Intégrations (1 semaine)
- JIRA tickets
- SonarQube sync
- SBOM generation

---

**Valeur ajoutée** :
- 🔒 Sécurité : détection proactive des vulnérabilités
- ⏱️ Gain : 2-3h/mois (veille manuelle éliminée)
- 📦 Propreté : dépendances à jour et nettoyées

**Date de dernière mise à jour** : Mars 2026
