# 🔐 Security Policy Generator

> **Commande** : `git-ia-security`  
> **Statut** : 📝 Idée à explorer  
> **Priorité** : 🟣 Basse  
> **Effort estimé** : 40 heures

---

## 📋 Vue d'ensemble

`git-ia-security` génère automatiquement des politiques de sécurité et scanne le code pour détecter les vulnérabilités.

---

## 🎯 Fonctionnalités principales

### 1. Génération de SECURITY.md
```bash
# Génère fichier SECURITY.md standard
git-ia-security scaffold --org MyCompany

# Contenu généré :
# - Versions supportées
# - Processus de signalement de vulnérabilités
# - Contact sécurité
# - SLA de réponse
```

**Exemple de SECURITY.md généré** :
```markdown
# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.x     | :white_check_mark: |
| 1.x     | :x:                |

## Reporting a Vulnerability

To report a security vulnerability, please email security@mycompany.com

**Do not** open a public issue.

We will respond within 48 hours.

## Security Best Practices

- Always use HTTPS
- Never commit secrets
- Use environment variables for credentials
- Enable 2FA on all accounts
```

---

### 2. Génération de SBOM
```bash
# Software Bill of Materials
git-ia-security generate-sbom --format cyclonedx --output sbom.json

# Inclut :
# - Liste complète des dépendances
# - Versions
# - Licences
# - CVE connus
```

---

### 3. Scan de secrets
```bash
# Détecte secrets hardcodés
git-ia-security scan --secrets

# Détecte :
# - API keys (AWS, GitHub, etc.)
# - Tokens (JWT, OAuth)
# - Mots de passe
# - Certificats privés
```

**Exemple de sortie** :
```
🔍 Scan de secrets

❌ 2 secrets détectés :

src/config.py:15
  AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
  💡 Utiliser variable d'environnement : os.getenv("AWS_ACCESS_KEY")

.env.example:8
  GITHUB_TOKEN = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  ⚠️  Fichier .env.example doit contenir des placeholders, pas de vraies valeurs

Actions recommandées :
1. Supprimer secrets du code
2. Révoquer les tokens exposés
3. Utiliser variables d'environnement
4. Ajouter .env au .gitignore
```

---

### 4. Scan de licences
```bash
# Vérifie compatibilité des licences
git-ia-security scan --licenses --policy .security-policy.yml

# Détecte :
# - Licences incompatibles (GPL vs propriétaire)
# - Licences manquantes
# - Risques légaux
```

---

### 5. Politique de dépendances
```bash
# Crée politique de dépendances
git-ia-security policy --create --type dependencies

# Fichier généré : .security-policy.yml
# allowed_licenses:
#   - MIT
#   - Apache-2.0
#   - BSD-3-Clause
# blocked_licenses:
#   - GPL-3.0
#   - AGPL-3.0
# max_severity_allowed: MODERATE
```

---

## 🔗 Intégrations

### 1. git-ia-deps
```bash
# Combine audit dépendances + sécurité
git-ia-deps audit && git-ia-security scan --secrets
```

### 2. CI/CD
```bash
# Pipeline de sécurité
git-ia-security scan --all --fail-on-critical
```

**Exemple GitLab CI** :
```yaml
security-scan:
  stage: security
  script:
    - git-ia-security scan --secrets --licenses --fail-on-critical
  only:
    - merge_requests
```

---

## 🎓 Exemples d'utilisation

### Scénario 1 : Préparation pour audit de sécurité

```bash
# 1. Génère politique de sécurité
git-ia-security scaffold --org MyCompany

# 2. Génère SBOM
git-ia-security generate-sbom --output sbom.json

# 3. Scan complet
git-ia-security scan --all

# 4. Rapport pour audit
git-ia-security report --output security-audit-report.pdf
```

---

### Scénario 2 : Détection de secrets avant commit

```bash
# Hook pre-commit
git-ia-security scan --secrets --staged-only

# Si secrets détectés :
# ❌ Commit bloqué
# 💡 Suggestions de correction affichées
```

---

## 🚀 Roadmap

### Phase 1 - MVP (2 semaines)
- Génération SECURITY.md
- Scan de secrets basique
- CLI basique

### Phase 2 - SBOM (1 semaine)
- Génération SBOM (CycloneDX, SPDX)
- Scan de licences
- Politique de dépendances

### Phase 3 - Intégrations (1 semaine)
- CI/CD checks
- git-ia-deps
- Rapports PDF

---

**Valeur ajoutée** :
- 🔒 Sécurité proactive
- 📋 Conformité réglementaire (SBOM requis)
- ⏱️ Gain : 2-3 jours pour audit de sécurité

**Date de dernière mise à jour** : Mars 2026
