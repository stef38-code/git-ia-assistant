# 🧪 Propositions de Nouveaux Scénarios - Git IA Assistant

> **Date** : Mars 2026  
> **Contexte** : Analyse des commandes existantes et identification des gaps pour un développeur full-stack (Java/Spring Boot, Angular, Python, Shell)

---

## 📊 État des Lieux

### Commandes actuellement implémentées (11)

| Commande | Fonction | Limites identifiées |
|----------|----------|---------------------|
| `git-ia-commit` | Messages de commit IA | Pas de hook pre-commit, pas de validation linters |
| `git-ia-test` | Génération de tests | Pas de couverture, pas de stub/mock auto |
| `git-ia-mr-review` | Revue MR/PR distante | Pas de suggestions inline applicables |
| `git-ia-refacto` | Refactorisation | Pas de linting auto-appliqué |
| `git-ia-doc` | Documentation | Pas de génération OpenAPI/Swagger |
| `git-ia-explain` | Explication de code | Pas de diagrammes |
| `git-ia-changelog` | Génération changelog | Pas d'intégration JIRA/tickets |
| `git-ia-squash` | Suggestion de squash | Pas de validation interactive |
| `git-ia-commit-version` | Commit + versioning | Pas de notes de release auto |

### Scénarios du laboratoire (3)

- ✅ **git/** - Commit avec versioning automatique (implémenté)
- 📝 **jira/** - Synchronisation Git ↔ JIRA

---

## 🎯 Nouveaux Scénarios Proposés

### 🔴 PRIORITÉ 1 : Lint & Format Intelligent

**Commande** : `git-ia-lint`

**Problème résolu** :
- Éliminer les aller-retours "fix linting" dans les reviews
- Appliquer automatiquement les règles de style
- Comprendre *pourquoi* une règle de linting existe

**Fonctionnalités** :
```bash
# Analyse et affiche les violations
git-ia-lint                                  # Auto-détecte le framework
git-ia-lint src/UserService.java             # Fichier spécifique

# Application automatique des corrections
git-ia-lint --apply                          # Corrige toutes les violations
git-ia-lint --apply --commit                 # + crée un commit "style: apply linting rules"

# Mode interactif avec explications IA
git-ia-lint --explain                        # L'IA explique chaque violation
git-ia-lint --ignore-rule no-console --apply # Ignore certaines règles
```

**Frameworks supportés** :
- **Python** : pylint, black, isort, flake8
- **Java** : checkstyle, spotless, google-java-format
- **TypeScript/JavaScript** : eslint, prettier
- **Shell** : shellcheck

**Intégrations** :
- Hook pre-commit : lance `git-ia-lint --apply` avant le commit
- CI/CD : `git-ia-lint --check` en mode read-only pour valider
- `git-ia-review` : affiche les violations de linting dans la review

**Valeur ajoutée** :
- ⏱️ Gain de temps : ~15 min/jour (pas de corrections manuelles)
- 📈 Qualité : respect automatique des conventions
- 🎓 Pédagogie : comprendre les règles (pas juste les appliquer)

**Fichier documentation** : `laboratoire/lint/outil_lint_format.md`

---

### 🟠 PRIORITÉ 2 : Génération de Composants Full-Stack

**Commande** : `git-ia-scaffold`

**Problème résolu** :
- Réduire le temps de setup pour nouveau code (50% du temps gagné)
- Respecter automatiquement les patterns du projet
- Générer code + tests + documentation en une commande

**Sous-scénarios** :

#### 2a. Spring Boot - Controller/Service/Entity

```bash
# Génération d'une entité JPA complète
git-ia-scaffold entity --name User --fields "id:Long,name:String,email:String" --jpa

# Résultat généré :
# - src/main/java/.../User.java (@Entity, @Id, getters/setters)
# - src/main/java/.../UserRepository.java (extends JpaRepository)
# - src/main/java/.../UserService.java (logique métier)
# - src/main/java/.../UserController.java (@RestController, CRUD endpoints)
# - src/test/java/.../UserControllerTest.java (tests JUnit 5 + MockMvc)
# - src/test/java/.../UserServiceTest.java (tests unitaires)

# Génération avec relations
git-ia-scaffold entity --name Order --belongs-to User --has-many OrderItem
```

#### 2b. Angular - Component/Service/Model

```bash
# Génération d'un composant avec features
git-ia-scaffold component --name UserList --features routing,reactive-forms,pipes

# Résultat généré :
# - user-list.component.ts (logique + OnInit)
# - user-list.component.html (template PrimeNG)
# - user-list.component.css (styles)
# - user-list.component.spec.ts (tests Jasmine)
# - user.service.ts (HttpClient CRUD)
# - user.model.ts (interface TypeScript)
# - app-routing.module.ts (mise à jour auto)

# Génération avec API backend
git-ia-scaffold component --name UserList --api http://localhost:8080/api/users
```

#### 2c. Python FastAPI - Route/Schema/Model

```bash
# Génération d'une route CRUD complète
git-ia-scaffold route --name users --methods GET,POST,PUT,DELETE --orm sqlalchemy

# Résultat généré :
# - app/schemas/user.py (Pydantic models)
# - app/models/user.py (SQLAlchemy ORM)
# - app/routes/users.py (FastAPI endpoints)
# - tests/test_users.py (tests pytest)
# - alembic/versions/xxx_create_users.py (migration)
```

**Options avancées** :
- `--template custom` : utilise templates projet spécifiques
- `--dry-run` : prévisualise le code généré
- `--with-swagger` : génère documentation OpenAPI
- `--ai-enhance` : enrichit avec suggestions IA (validation, sécurité)

**Intégrations** :
- `git-ia-test` : génère tests supplémentaires
- `git-ia-doc` : documente les composants générés
- `git-ia-commit` : commit automatique avec message structuré

**Valeur ajoutée** :
- ⏱️ Gain : 30-60 min par composant
- 🎯 Cohérence : patterns projet respectés
- 🧪 Tests inclus : couverture immédiate

**Fichier documentation** : `laboratoire/scaffold/outil_scaffold_composants.md`

---

### 🟡 PRIORITÉ 3 : Coverage & Test Assistant

**Commande** : `git-ia-coverage`

**Problème résolu** :
- Identifier rapidement les zones non testées
- Générer automatiquement les tests manquants
- Atteindre seuils de couverture requis (80%, 90%)

**Fonctionnalités** :

```bash
# Analyse de la couverture
git-ia-coverage analyze                      # Détecte coverage.xml, jacoco, pytest
git-ia-coverage analyze --threshold 80       # Fail si < 80%
git-ia-coverage analyze --report html        # Génère rapport HTML

# Affichage des fichiers sous-couverts
git-ia-coverage show --below 70              # Liste fichiers < 70%
git-ia-coverage show --file src/UserService.java  # Détails par fichier

# Génération automatique de tests
git-ia-coverage generate --file src/UserService.java --target 90
# → Analyse les branches/lignes non couvertes
# → Génère tests pour les edge cases manquants
# → Demande confirmation avant création

# Mode interactif
git-ia-coverage generate --interactive
# → Affiche chaque test suggéré
# → Demande validation : [y: créer, n: skip, e: éditer, a: créer tous]

# Intégration CI/CD
git-ia-coverage check --fail-under 80        # Exit code 1 si < 80%
```

**Formats supportés** :
- **Java** : JaCoCo XML, Cobertura
- **Python** : coverage.xml (pytest-cov)
- **JavaScript/TypeScript** : Istanbul/NYC JSON
- **Angular** : Karma coverage

**Intégrations** :
- **JIRA** : crée ticket si couverture < seuil (`git-ia-coverage jira-ticket`)
- `git-ia-test` : génère tests complémentaires

**Exemple de sortie** :

```
📊 Analyse de couverture terminée

Fichiers sous le seuil (80%) :
┌─────────────────────────────────┬──────────┬───────────┐
│ Fichier                         │ Coverage │ Manquants │
├─────────────────────────────────┼──────────┼───────────┤
│ src/UserService.java            │ 65%      │ 12 lignes │
│ src/OrderController.java        │ 72%      │ 8 lignes  │
│ src/utils/DateHelper.java       │ 45%      │ 20 lignes │
└─────────────────────────────────┴──────────┴───────────┘

💡 Suggestion IA :
   - UserService.java : manque tests pour cas d'erreur (null, exceptions)
   - DateHelper.java : aucun test pour formatage dates futures

Générer les tests manquants ? [y/n] : y
✅ 5 nouveaux tests créés dans src/test/java/...
```

**Valeur ajoutée** :
- 🎯 Cibles précises : sait exactement quoi tester
- ⏱️ Gain : 1-2h par module
- ✅ Qualité : atteint critères requis

**Fichier documentation** : `laboratoire/coverage/outil_coverage_tests.md`

---

### 🟢 PRIORITÉ 4 : Gestion des Dépendances Intelligente

**Commande** : `git-ia-deps`

**Problème résolu** :
- Détecter proactivement les vulnérabilités (CVE)
- Upgrader les dépendances de manière sécurisée
- Nettoyer les dépendances inutilisées

**Fonctionnalités** :

```bash
# Audit de sécurité
git-ia-deps audit                            # SBOM + CVE scan
git-ia-deps audit --show-vulnerabilities     # Affiche uniquement les vulns
git-ia-deps audit --severity critical        # Filtre par criticité

# Upgrade sécurisé
git-ia-deps upgrade --safe                   # Patch + Minor uniquement (SemVer)
git-ia-deps upgrade --major --confirm        # Inclut Major avec confirmation
git-ia-deps upgrade --dep lodash --to 4.17.21  # Upgrade spécifique

# Nettoyage
git-ia-deps check --unused                   # Détecte imports/dépendances inutilisés
git-ia-deps check --unused --remove-prompt   # Propose suppression interactive
git-ia-deps check --duplicates               # Détecte versions multiples (npm/maven)

# Création de PR/MR automatique
git-ia-deps upgrade --safe --create-mr       # Crée MR avec changelog
git-ia-deps audit --fix-vulns --create-mr    # Fix vulns + MR

# Rapport
git-ia-deps report --format markdown         # Génère DEPENDENCIES.md
git-ia-deps report --sbom                    # Génère Software Bill of Materials
```

**Langages supportés** :
- **Java** : pom.xml (Maven), build.gradle (Gradle)
- **Node.js** : package.json, package-lock.json
- **Python** : requirements.txt, pyproject.toml, Pipfile

**Intégrations API** :
- `npm audit` / `yarn audit`
- `pip-audit` / `safety`
- `gradle dependencyCheck` / `maven-dependency-plugin`
- OWASP Dependency-Check
- Snyk API (optionnel)
- GitHub Advisory Database

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
   - spring-web : upgrade vers 5.3.9 (patch Spring Boot requis)
   - axios : upgrade vers 0.21.4 (pas de breaking change)

Appliquer les corrections ? [y: oui, n: non, c: créer MR] : c
✅ MR créée : 'fix(deps): upgrade dependencies to fix 3 CVEs'
   → https://gitlab.com/project/merge_requests/123
```

**Intégrations** :
- `git-ia-commit` : commit automatique des upgrades
- `git-ia-changelog` : enregistre les changements de dépendances
- **JIRA** : crée tickets pour vulnérabilités critiques

**Valeur ajoutée** :
- 🔒 Sécurité : détection proactive des vulnérabilités
- ⏱️ Gain : 2-3h/mois (veille manuelle éliminée)
- 📦 Propreté : dépendances à jour et nettoyées

**Fichier documentation** : `laboratoire/dependencies/outil_dependances_intelligentes.md`

---

### 🔵 PRIORITÉ 5 : Documentation API Auto-Sync

**Commande** : `git-ia-api-doc`

**Problème résolu** :
- Documentation API toujours à jour (synchronisée avec le code)
- Génération automatique de spec OpenAPI/Swagger
- Création de client SDK TypeScript depuis spec backend

**Fonctionnalités** :

```bash
# Génération de spec OpenAPI
git-ia-api-doc generate --source src/controllers --format openapi-3.0 --output docs/api.yaml

# Enrichissement avec IA
git-ia-api-doc enrich --spec docs/api.yaml --add-examples --add-descriptions

# Génération de documentation Markdown
git-ia-api-doc markdown --spec docs/api.yaml --output docs/API.md

# Synchronisation avec JIRA
git-ia-api-doc sync-jira --auto-create-stories  # Crée story par endpoint

# Génération de client SDK
git-ia-api-doc generate-client --spec docs/api.yaml --lang typescript --output src/sdk/

# Validation
git-ia-api-doc validate --spec docs/api.yaml --strict
```

**Frameworks supportés** :

#### Java/Spring Boot
```bash
# Scan automatique des annotations Spring
git-ia-api-doc generate --auto-detect spring-boot

# Détecte :
# - @RestController, @GetMapping, @PostMapping
# - @RequestBody, @PathVariable, @RequestParam
# - @ApiOperation, @ApiResponse (Swagger annotations)

# Génère OpenAPI avec :
# - Endpoints, méthodes HTTP, chemins
# - Schémas (depuis POJO Java)
# - Codes d'erreur, authentification (JWT, OAuth2)
# - Exemples de requêtes/réponses
```

#### Angular
```bash
# Génération de client TypeScript depuis spec backend
git-ia-api-doc generate-client --spec backend/api.yaml --lang typescript --output src/app/sdk/

# Résultat :
# - api/user.service.ts (méthodes typées HttpClient)
# - models/user.model.ts (interfaces TypeScript)
# - api.module.ts (injection de dépendances)

# Mock automatique pour tests
git-ia-api-doc generate-mocks --spec backend/api.yaml --output src/app/testing/
```

#### Python/FastAPI
```bash
# Enrichissement du schema auto-généré par FastAPI
git-ia-api-doc enrich --framework fastapi --add-ai-descriptions

# Ajoute :
# - Descriptions détaillées des endpoints (par IA)
# - Exemples de requêtes/réponses
# - Codes d'erreur documentés
# - Best practices de consommation
```

**Intégrations** :
- **JIRA** : crée stories pour chaque endpoint (`POST /users` → story "Implémenter création utilisateur")
- **GitLab Wiki** : push auto vers wiki
- **Confluence** : export vers Confluence
- `git-ia-changelog` : documente changements d'API

**Exemple de sortie** :

```
📄 Génération de documentation API

✅ 12 endpoints détectés :
   - GET    /api/users
   - POST   /api/users
   - GET    /api/users/{id}
   - PUT    /api/users/{id}
   - DELETE /api/users/{id}
   ...

🤖 Enrichissement IA en cours...
   ✅ Descriptions ajoutées (12/12)
   ✅ Exemples générés (12/12)
   ✅ Codes d'erreur documentés (12/12)

📝 Fichiers générés :
   - docs/api.yaml (OpenAPI 3.0, 450 lignes)
   - docs/API.md (Markdown, 200 lignes)
   - src/sdk/typescript/api/user.service.ts
   - src/sdk/typescript/models/user.model.ts

🔗 Synchronisation JIRA :
   → 12 stories créées dans projet MYAPP
   → Labels : api, backend, documentation
```

**Valeur ajoutée** :
- 📚 Documentation toujours à jour
- ⏱️ Gain : 4-6h par sprint (doc manuelle éliminée)
- 🔗 Synchronisation backend ↔ frontend automatique

**Fichier documentation** : `laboratoire/api-doc/outil_api_documentation.md`

---

## 🔗 Synergies avec l'Existant

| Nouveau Scénario | Intégrations |
|------------------|--------------|
| **Lint** | `git-ia-commit` (pre-hook), `git-ia-review` (analyse linting) |
| **Scaffold** | `git-ia-test` (tests), `git-ia-doc` (docs), `git-ia-commit` (commit auto) |
| **Coverage** | `git-ia-test` (génération tests), **JIRA** (tickets si < seuil) |
| **API-Doc** | `git-ia-doc` (enrichit), **JIRA** (stories), `git-ia-commit-version` (versioning API) |

---

## 💡 Scénarios Bonus (Opportunités Long Terme)

### 6. Migration de Code Inter-Framework
**`git-ia-migrate`**
```bash
git-ia-migrate --from jest --to vitest
git-ia-migrate --from swagger-2.0 --to openapi-3.0
git-ia-migrate --from angularjs --to angular --version 17
```

### 7. Performance Audit + Suggestions
**`git-ia-perf`**
```bash
git-ia-perf analyze --file src/HeavyAlgo.java --profile time,memory
git-ia-perf suggest --threshold 500ms --optimize
```

### 8. Security Policy Generator
**`git-ia-security`**
```bash
git-ia-security scaffold --org MyCompany --generate-sbom --policy dependencies
git-ia-security scan --secrets --licenses --vulnerabilities
```

### 9. Database Schema Management
**`git-ia-db`**
```bash
git-ia-db generate-migration --from old_schema.sql --to new_schema.sql
git-ia-db explain-migration --file alembic/versions/xxx.py
git-ia-db rollback-plan --migration xxx
```

### 10. CI/CD Pipeline Generator
**`git-ia-cicd`**
```bash
git-ia-cicd generate --platform github-actions --stages build,test,deploy
git-ia-cicd analyze --file .github/workflows/ci.yml --optimize
```

---

## 📊 Priorisation Recommandée

### Phase 1 - Quick Wins (2-3 mois)
1. ✅ **Lint & Format** (40h) - Valeur immédiate, faible complexité
2. ✅ **Coverage** (30h) - Critères qualité, facile à implémenter

### Phase 2 - High Value (3-6 mois)
3. ✅ **Deps** (50h) - Sécurité proactive, ROI élevé
4. ✅ **API-Doc** (60h) - Synergies multiples, demande récurrente

### Phase 3 - Complex Features (6-12 mois)
5. ✅ **Scaffold** (80h) - Valeur majeure, templates complexes

### Phase 4 - Long Terme (12+ mois)
6. 🔄 **Migrate, Perf, Security, DB, CI/CD** - Selon besoins métier

---

## 📝 Prochaines Étapes

1. **Validation** : Choisir 1-2 scénarios à documenter en détail
2. **Documentation** : Créer fichiers `.md` dans `laboratoire/<scenario>/`
3. **Prototypage** : Implémenter MVP pour valider faisabilité
4. **Intégration** : Connecter avec commandes existantes

---

**Date de dernière mise à jour** : Mars 2026  
**Contributeur** : Analyse automatique basée sur profil développeur full-stack
