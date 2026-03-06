# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
et ce projet adhère à [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2026-03-06

### Ajouté
- **Documentation complète du laboratoire** : 13 scénarios de fonctionnalités documentés dans `laboratoire/`
  - 🔴 **Priorité Haute (Quick Wins)** :
    - `git-ia-lint` : Linting intelligent avec explications IA (40h) - Auto-détection pylint/eslint/spotless/shellcheck, corrections automatiques, pre-commit hook
    - `git-ia-coverage` : Assistant de couverture de tests (30h) - Analyse JaCoCo/pytest-cov/Istanbul, génération auto de tests manquants
  - 🟠 **Priorité Moyenne** :
    - `git-ia-scaffold` : Génération de composants full-stack (80h) - Spring Boot/Angular/FastAPI avec tests et documentation
    - `git-ia-deps` : Gestion intelligente des dépendances (50h) - Audit CVE, upgrade sécurisé SemVer, nettoyage, création MR/PR automatique
    - `git-ia-api-doc` : Documentation API auto-sync (60h) - Génération OpenAPI 3.0, client SDK TypeScript/Java/Python, sync JIRA
  - 🟣 **Long Terme** :
    - `git-ia-migrate` : Migration inter-framework (60h) - Jest→Vitest, Swagger→OpenAPI, Angular 15→17
    - `git-ia-perf` : Audit de performance (50h) - Détection goulots, suggestions optimisation IA
    - `git-ia-security` : Politique de sécurité (40h) - Génération SECURITY.md, SBOM, scan secrets
    - `git-ia-db` : Gestion schémas DB (50h) - Génération migrations, validation DB↔ORM
    - `git-ia-cicd` : Génération pipelines CI/CD (70h) - GitHub Actions/GitLab CI/Jenkins avec optimisation
- **Fichier PROPOSITIONS.md** : Analyse détaillée de 10 nouveaux scénarios avec ROI, synergies et roadmap d'implémentation
- **Section README.md "Laboratoire"** : +200 lignes documentant tous les scénarios avec tableau récapitulatif (priorités, efforts, ROI)
- **Documentation existante enrichie** :
  - Scénario SonarQube : Intégration complète avec suggestions IA de corrections
  - Scénario JIRA : Synchronisation Git↔JIRA, TODO→tickets, rapports de sprint
  - Scénario Commit+Version : Workflow automatisé (déjà implémenté)

### Amélioré
- **Estimation d'effort** : ~580h total pour tous les scénarios (Quick Wins : 70h, High Value : 190h, Long Terme : 320h)
- **ROI documenté** : Break-even à ~7 mois (1 dev) ou ~1 mois (équipe de 5 devs)
- **Synergies identifiées** : Intégrations entre scénarios (lint↔commit, coverage↔test, deps↔changelog, etc.)

## [0.4.0] - 2026-03-06

### Ajouté
- **Détection automatique des frameworks** : Les commandes `git-ia-review` et `git-ia-mr` détectent maintenant les frameworks utilisés
  - Analyse automatique des fichiers de dépendances (pom.xml, package.json, requirements.txt, etc.)
  - Support Java (Spring Boot, Quarkus, Hibernate, JUnit, AssertJ)
  - Support JavaScript/TypeScript (Angular avec version, React, Vue, Express, NestJS, PrimeNG, Jest, Playwright)
  - Support Python (Django, Flask, FastAPI, PyTest, SQLAlchemy)
  - Support PHP (Laravel, Symfony), Ruby (Rails, Sinatra), Go (Gin, Echo, Fiber)
  - Support Rust (Actix-web, Rocket), .NET (ASP.NET Core, Entity Framework Core)
  - Affichage dans le prompt : "Java / Spring Boot, Hibernate, AssertJ" ou "TypeScript / Angular 17, PrimeNG, Jest"
- **Wrapper interactif `ia` avec fzf** : Menu interactif pour sélectionner visuellement les commandes
  - Création automatique du script `~/.local/share/scripts/ia.sh` lors de l'installation
  - Lien symbolique `~/.local/bin/ia` (remplacé à chaque installation)
  - Preview en temps réel affichant le `--help` de la commande sélectionnée
  - Navigation au clavier (↑/↓/Enter/Esc) avec thème coloré Dracula
  - Mode direct : `ia git-ia-commit --help` ou `ia git-ia-review fichier.py`
  - Détection automatique de fzf avec instructions d'installation si manquant
- **Nouvelle commande `git-ia-commit-version`** : Workflow automatisé de commit avec versioning
  - Génération du message de commit avec IA
  - Détection automatique du type de projet (Python, Java, Node.js, Go, Rust, .NET)
  - Incrémentation automatique de version selon SemVer (feat→MINOR, fix→PATCH, BREAKING→MAJOR)
  - Mise à jour automatique du CHANGELOG.md
  - Mise à jour du fichier de version (pyproject.toml, pom.xml, package.json, Cargo.toml, *.csproj)
  - Support des options `--dry-run`, `--no-version`, `--no-changelog`
  - Alias : `ia-commit-version`
- **Documentation du workflow** : Fichier `outil_commit_developpement.md` décrivant le processus complet
- **Dépendances** : Ajout de `tomli_w` pour l'écriture de fichiers TOML

### Corrigé
- **Git push avec nouvelles branches** : Détection automatique de l'absence d'upstream et ajout de `--set-upstream origin <branche>`
- **Détection de HEAD détaché** : Bloque le push avec message d'erreur explicite si en mode détaché
- **Message "Aucun fichier spécifié"** : N'affiche plus ce message si aucun fichier n'est détecté

### Amélioré
- **Refactoring `review_my_code_cli.py`** : Découpage de la fonction main() en 6 fonctions thématiques
  - Réduction de main() de 108 → 45 lignes (-58%)
  - Amélioration de la lisibilité et testabilité
  - Mutualisation de 5 fonctions Git dans `python_commun/git/git_core.py`

## [0.3.0] - 2026-03-06

### Ajouté
- **Tests unitaires manquants** : Le prompt de revue MR/PR suggère automatiquement des tests unitaires avec :
  - Nom du test + Scénario + Comportement attendu + Données de test + Exemple de code
  - Format Given/When/Then (Arrange/Act/Assert)
  - Adaptation au framework de test (PyTest, JUnit, Jest, etc.)
  - 5 critères pour suggérer des tests (nouvelle logique, API publiques, cas limites, gestion d'erreurs, logique complexe)

- **Tests de sécurité automatiques** : Le prompt de revue MR/PR détecte les vulnérabilités et suggère des tests de sécurité :
  - Couverture OWASP Top 10 (Injection SQL, XSS, Auth, Path Traversal, Data Exposure, CORS)
  - Format identique aux tests unitaires avec payload d'attaque
  - 10 critères de détection de vulnérabilités
  - Exemples de tests pour 6 types de vulnérabilités

- **Détection automatique du langage** : Le prompt de revue MR/PR utilise désormais `detect_lang_repo()` pour s'adapter au langage du projet
  - Placeholder `{langage}` ajouté au template
  - Support Python, Java, Angular, et autres langages détectés

- **Documentation complète** : Nouveau README.md dans `prompts/` documentant :
  - Structure des 4 catégories (commits, review, code_quality, git_history)
  - Utilisation des placeholders
  - Guide d'ajout de nouveaux prompts

### Changé
- **Refonte complète du prompt MR/PR** (`mr_review_prompt.md`) :
  - 68 → 244 lignes (+259%)
  - 8 sections structurées avec emojis (⚠️ 🐛 🚀 🛠️ ✅ 🚫 ✨ 📊)
  - Niveaux de risque définis (FAIBLE/MOYEN/ÉLEVÉ/CRITIQUE)
  - Section sécurité enrichie (11 → 42 lignes, +282%)
  - Section tests enrichie (6 → 34 lignes)
  - Template de réponse Markdown standardisé
  - Élimination de toutes les données privées (références Jenkins/Vault)

- **Réorganisation des prompts** :
  - Structure hiérarchique en 4 sous-répertoires thématiques
  - `commits/` : commit_message, optimise_commit, squash (3 fichiers)
  - `review/` : python, java, angular, mr_review (4 fichiers)
  - `code_quality/` : test_generation, doc_generation, refacto (3 fichiers)
  - `git_history/` : changelog, explain (2 fichiers)
  - 41 fichiers Python mis à jour pour les nouveaux chemins
  - `pyproject.toml` : package-data avec sous-répertoires

- **Renommage** :
  - `mr_cli.py` → `mr_review_cli.py` (nom plus explicite)
  - `debug/mr_cli/` → `debug/mr_review_cli/`
  - Point d'entrée `pyproject.toml` mis à jour

- **Déplacement de review_prompt.py** :
  - `prompts/review_prompt.py` → `core/utils/review_prompt.py`
  - Séparation claire : templates (.md) vs code (.py)
  - Création du répertoire `core/utils/` pour les utilitaires

### Corrigé
- Chemins relatifs dans `review_prompt.py` pour charger les templates depuis `core/utils/`
- Chemins d'imports dans 41 fichiers Python suite à la réorganisation des prompts

## [0.2.1] - 2026-02-22

### Ajouté
- Option `--optimise` dans `git-ia-commit` pour regrouper les changements en commits logiques et atomiques.
- Option `--partiel` dans `git-ia-commit` (nécessite `--optimise`) permettant d'utiliser `git add -p` pour répartir un fichier sur plusieurs commits.

### Changé
- Refactorisation de `git_core.py` : Centralisation des appels `GitPython` (reset, push, commit, index status).
- Amélioration de `system.py` : La fonction `executer_capture` supporte désormais l'envoi de données via `stdin`.
- `git-ia-commit` utilise désormais exclusivement les fonctions de `git_core.py` pour manipuler le dépôt Git.

## [0.2.0] - 2026-02-22

### Ajouté
- Nouveaux outils d'assistance IA :
    - `ia-explain` : Explique le code source de manière pédagogique.
    - `ia-test` : Génère des suites de tests (PyTest, JUnit, Jest, Vitest, Playwright).
    - `ia-doc` : Génère de la documentation technique (Markdown, Javadoc, KDoc, Docstrings).
    - `ia-refacto` : Propose des refactorisations intelligentes du code.
- Mode interactif dans `ia-commit` pour affiner le message généré via une instruction utilisateur.
- Analyse de sécurité et évaluation du risque (1-10) dans `ia-mr`.
- Extraction de contexte automatique pour les fichiers importés localement dans `ia-review` (support initial pour Python).
- Support complet de Gemini, Copilot et Ollama pour tous les nouveaux outils.

### Changé
- Refactorisation majeure de la structure interne pour une meilleure modularité des assistants.
- Amélioration de la robustesse du chargement des prompts grâce à un chemin centralisé.

## [0.1.3] - 2026-02-22

### Changé
- Amélioration de la gestion des imports dans les scripts CLI pour inclure correctement la librairie `python_commun`.
- Mise à jour de la configuration IntelliJ (`git-ia-assistant.iml`) pour déclarer `src` et `libs/python_commun/src` comme racines de sources, résolvant les erreurs "Unresolved reference".

## [0.1.2] - 2026-02-22

### Changé
- Refactorisation du script `install.sh` avec l'utilisation de fonctions pour une meilleure lisibilité.
- Ajout de la gestion automatique des alias dans `~/.aliases`. Les alias suivent le format `ia-xxxxx` (ex: `ia-commit`).
- Amélioration des messages de fin d'installation concernant la configuration du PATH et des alias.

## [0.1.1] - 2026-02-22

### Ajouté
- Amélioration du script d'installation `install.sh` pour supporter l'exécution directe via `curl -fsSL ... | bash`.
- Mise à jour du `README.md` avec les instructions d'installation rapide.

## [0.1.0] - 2026-02-22

### Ajouté
- Initialisation du projet `git-ia-assistant`.
- Outil de génération de messages de commit (`git-ia-commit`).
- Outil de revue de code locale (`git-ia-review`).
- Outil de revue de Merge/Pull Request (`git-ia-mr`).
- Aide à la stratégie de squash (`git-ia-squash`).
- Générateur de changelog automatique (`git-ia-changelog`).
- Script d'installation `install.sh` pour une installation utilisateur isolée.
- Documentation initiale dans `README.md`.
- Intégration de la bibliothèque partagée `python_commun`.
