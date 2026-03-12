# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
et ce projet adhère à [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.9.8] - 2026-03-12

### Corrigé
- **`McpConfigManager`** : Correction du serveur MCP `git` — le package `@modelcontextprotocol/server-git` n'existe pas sur npm. Remplacement par `mcp-server-git` (package Python officiel), lancé via `uvx mcp-server-git`.

### Ajouté
- **Vérification des serveurs MCP** : Nouvelle méthode statique `McpConfigManager.verifier_installation()`.
  - Détecte automatiquement le type de lanceur (`uvx` pour les packages Python, `npx` pour les packages npm).
  - Vérifie la présence de `npx`/`node` (Node.js ≥ 18) et de `uvx`/`uv` dans le PATH.
  - Contrôle l'installation de chaque package via `npm list -g` (npm) et `pip show` (Python).
  - Affiche un message d'erreur détaillé avec les commandes d'installation pour chaque serveur manquant.
  - Vérifie la présence des variables d'environnement requises (`GITHUB_PERSONAL_ACCESS_TOKEN`, `GITLAB_PRIVATE_TOKEN`, `SONAR_TOKEN`).
- **`INSTALLATION_INSTRUCTIONS`** : Dictionnaire centralisé des instructions d'installation pour chacun des 9 serveurs MCP supportés.

## [0.9.7] - 2026-03-11

### Ajouté
- **Enrichissement des serveurs MCP** : Ajout des serveurs `filesystem` et `search` (ripgrep) pour permettre à l'IA d'analyser l'intégralité du code source et d'effectuer des recherches textuelles performantes.
- **Sécurisation MCP** : Restriction automatique des accès `filesystem` et `search` au seul répertoire du dépôt cloné (`repo_path`).

### Amélioré
- **`git-ia-mr`** : Passage automatique du contexte local (`repo_path`) au gestionnaire de configuration MCP pour une analyse d'impact plus profonde.


## [0.9.6] - 2026-03-11

### Ajouté
- **Suite de tests unitaires** : Création des premiers tests unitaires pour `IaAssistantMr` et `IaAssistantMrFactory`.
  - Couverture de la sélection de prompt (langage seul, IA spécifique, générique).
  - Validation de l'extraction de la version cible (migration et projet).
  - Validation de l'instanciation via la Factory.
- **Dépendances de développement** : Ajout de `pytest` et `pytest-mock` dans `optional-dependencies`.

## [0.9.5] - 2026-03-11

### Ajouté
- **Support natif des serveurs MCP (Model Context Protocol)** :
  - Nouvelle option `--mcp` pour `git-ia-mr`.
  - Génération dynamique d'une configuration MCP (`mcp-config.json`) basée sur le contexte.
  - Support des serveurs : `git`, `github`/`gitlab`, `sequential-thinking`, `typescript`, `angular` et `sonarqube`.
  - Intégration directe avec Copilot CLI via le flag `--additional-mcp-config`.
- **Répertoire dédié MCP** : Centralisation de la logique dans `cli/mcp/` avec le `McpConfigManager`.
- **Prompt Angular Gemini optimisé** : Nouveau prompt `mr_review_angular_gemini_prompt.md` incluant des instructions de "Chain of Thought" pour exploiter le contexte étendu.

### Amélioré
- **`python_commun`** : Mise à jour de `envoyer_prompt_copilot` pour supporter les configurations MCP externes.

## [0.9.4] - 2026-03-11

### Ajouté
- **Spécialisation des prompts par modèle IA** : Support de prompts dédiés selon l'IA utilisée (Gemini, Copilot, Ollama).
  - Priorité de recherche : `{langage}_{ia}_prompt.md` -> `{langage}_prompt.md` -> `mr_review_{ia}_prompt.md` -> prompt générique.
  - Ajout du prompt spécialisé `mr_review_angular_gemini_prompt.md` exploitant la fenêtre de contexte étendue de Gemini (Chain of Thought).
- **Refactoring Factory** : Introduction de `IaAssistantMrFactory.create_mr_instance` pour une instanciation centralisée et typée, gérant l'injection du nom de l'IA.

### Amélioré
- **Sélection dynamique du prompt pour Ollama** : Utilise désormais `_choisir_prompt_mr()` au lieu d'un prompt générique hardcodé, permettant de bénéficier des prompts spécialisés par langage.

## [0.9.3] - 2026-03-10

### Ajouté
- **Prompts MR spécialisés par langage** : `git-ia-mr` sélectionne automatiquement le prompt adapté au langage détecté
  - `mr_review_java_prompt.md` : critères Spring Security, JPA/Hibernate N+1, `@Transactional`, Records, Jakarta EE
  - `mr_review_python_prompt.md` : critères type hints, mutable defaults, context managers, `async/await`, PyTest
  - `mr_review_angular_prompt.md` : critères memory leaks RxJS, XSS/DomSanitizer, Signals, `OnPush`, `trackBy`
  - Fallback automatique sur le prompt générique pour les autres langages (Go, PHP, etc.)
- **`IaAssistantMr._choisir_prompt_mr()`** : méthode de sélection du prompt basée sur le langage détecté

## [0.9.2] - 2026-03-10

### Corrigé
- **`git-ia-mr` hors dépôt Git** : l'exécution depuis un répertoire non-git échouait avec "Le répertoire actuel n'est pas un dépôt Git."
  - `IaAssistant.__init__()` accepte maintenant `require_repo: bool = True`
  - `IaAssistantMr` passe `require_repo=False` car la revue MR/PR fonctionne entièrement via URL distante

## [0.9.1] - 2026-03-09

### Corrigé
- **`install.sh` : parsing des arguments manquant** — les options `-r`, `--dry-run`, `-d` étaient
  silencieusement ignorées, rendant le remplacement d'installation non fonctionnel

### Amélioré
- **`install.sh` : refonte complète de la gestion des arguments** :
  - Ajout du parsing d'options via `case` : `-h/--help`, `--dry-run`, `-r/--replace`, `-d/--delete`
  - Nouvelle fonction `delete_installation()` : supprime le venv et les symlinks existants avant réinstallation
  - Option `--force-reinstall` systématique sur `pip install .` pour garantir la régénération des scripts d'entrée
  - Mode `--dry-run` : simulation complète sans aucune modification du système
  - Option `-d/--delete` : désinstallation complète du répertoire d'installation

## [0.9.0] - 2026-03-09

### Ajouté
- **Publication automatique du rapport de revue dans la MR/PR** :
  - Nouvelle option `--publier` pour `git-ia-mr`
  - Publication directe du rapport comme commentaire dans GitLab ou GitHub
  - Support complet des deux plateformes (notes GitLab, issue comments GitHub)
  - Header automatique "🤖 Revue automatique par IA" sur les commentaires
  - Gestion robuste des erreurs (permissions, authentification)
  - Messages informatifs en cas d'échec
  - Compatible avec mode `--dry-run` pour simulation
- **Nouvelle fonction `publier_commentaire_mr()` dans `python_commun.vcs.mr_utils`** :
  - API unifiée pour GitLab et GitHub
  - Validation du token et du contenu
  - Retour booléen pour succès/échec
  - Logging détaillé avec liens directs vers la MR/PR

### Amélioré
- **Workflow de revue amélioré** :
  - Sauvegarde locale + publication optionnelle du rapport
  - Continuité en cas d'échec de publication (rapport local conservé)
  - Notifications automatiques aux participants de la MR/PR

## [0.8.0] - 2026-03-09

### Ajouté
- **Détection automatique de migration de version** dans `git-ia-mr` :
  - Détection intelligente des migrations entre branches (ex: Python 3.8→3.12, Angular 14→20)
  - Support de 5 langages/frameworks : Python, Java, Node.js, Angular, React
  - Affichage console avec emoji 🔄 lors de la détection
  - Enrichissement automatique du prompt IA avec contexte de migration
  - Section dédiée dans le prompt : "🔄 Critères spécifiques en cas de migration"
  - Export du prompt généré vers `/home/appuser/ia_assistant/mrOrpr/prompt_genere_mr{N}.md` pour debug
- **Adaptation automatique du langage/framework détecté** :
  - Remplacement intelligent de la version source par la version de destination
  - Expert IA configuré sur la version cible (ex: "Expert en Angular 20" au lieu de "Angular 14")
  - Format d'expertise amélioré : "Java, Spring Boot, Hibernate" au lieu de "Java / Spring Boot, Hibernate"
- **Protection contre les MR volumineuses** dans `git-ia-mr` :
  - Analyse automatique de la volumétrie (fichiers, lignes, tokens estimés)
  - Limites par IA : Copilot (100K tokens), Gemini (800K tokens), Ollama (50K tokens)
  - Trois niveaux de protection :
    - < 70% limite : Continue sans warning
    - 70-100% : Avertissement avec estimation de temps/coût
    - > 100% : Rejet avec suggestions (utiliser Gemini, découper la MR, exclure fichiers générés)
  - Messages d'aide proactifs avec solutions concrètes
  - Estimation du coût pour Gemini (~$0.15 par million de tokens)
- **Harmonisation complète des logs** :
  - Tous les messages utilisent le format emoji (ℹ INFO:, ✅ SUCCÈS:, ❌ ERREUR:)
  - Suppression des messages redondants
  - Suppression des lignes vides inutiles
- **Nettoyage des réponses Copilot** :
  - Filtrage automatique des messages de débogage (`● Confirm working context`, `$ echo`, etc.)
  - Documents de revue propres sans pollution de debug

### Amélioré
- **Filtrage des fichiers ignorés dans `git-ia-commit`** :
  - Double vérification avec `git check-ignore` et `git add --dry-run`
  - Filtrage automatique des fichiers dans `.idea/`, `.venv/`, `cli/sonar/`, etc.
  - Message informatif lors du filtrage
  - Plus d'erreurs Git lors du commit avec fichiers ignorés
- **Migration du code vers `python_commun`** :
  - Module `vcs.version_detection` pour réutilisabilité cross-projet
  - Fonctions d'extraction par langage (Strategy pattern)
- **Mise à jour de `python_commun` vers v0.3.0** :
  - Nouvelles fonctions de détection de versions
  - Nettoyage automatique des réponses Copilot

### Changé
- **Format des informations de migration** dans les prompts :
  - Mise en forme simplifiée : `* Version source Angular : 14.3` (sans indentation excessive)
  - Suppression du mot "version" redondant dans les valeurs
- **Affichage de l'expertise** dans les prompts :
  - Format fluide : "Expert en Java, Spring Boot, Hibernate" (virgules au lieu de slashes)
  - Tous les frameworks sont inclus dans la description de l'expertise

### Corrigé
- **Bug d'inversion des versions** : Les versions source/cible étaient inversées (affichait 20.3→14.3 au lieu de 14.3→20.3)
- **Bug KeyError 'version_source'** : Template de prompt utilisait des placeholders qui causaient des erreurs de formatage
- **Bug TypeError log_debug()** : Mauvais nombre d'arguments dans les appels de logging
- **Bug InvalidGitRepositoryError** : Chemin Git dupliqué lors du clonage de MR
- **Bug filtrage .gitignore** : Les fichiers dans répertoires ignorés (`.idea/`) causaient des erreurs Git

### Sécurité
- **Prévention des dépassements de limites d'API** : La vérification de volumétrie empêche les erreurs "context length exceeded"
- **Contrôle des coûts** : Estimation du coût avant envoi pour Gemini
- **Expérience utilisateur prévisible** : Pas de timeouts inexpliqués ou d'erreurs cryptiques

### Dépendances
- Mise à jour `python_commun` de 0.2.0 à 0.3.0

## [0.7.0] - 2026-03-08

### Changé
- **Réorganisation du répertoire `cli/`** : Les scripts ont été déplacés dans des sous-répertoires thématiques (`commits/`, `review/`, `code_quality/`, `git_history/`) pour une meilleure symétrie avec les prompts et une architecture plus propre.
- **Refonte de la documentation** : Le fichier `README.md` a été découpé en plusieurs documents spécialisés dans le dossier `doc/` pour améliorer la lisibilité.

### Amélioré
- **Gestion des fichiers supprimés** : 
  - `python_commun` : La fonction `liste_fichier_non_suivis_et_modifies` détecte désormais correctement les fichiers supprimés (`git rm` ou suppression manuelle).
  - `IaAssistantCommit` : Le moteur de commit autorise désormais l'ajout de suppressions de fichiers suivis à l'index Git, résolvant les blocages lors du nettoyage de projet.
- **Configuration du Menu** : Mise à jour de `ia_menu.yaml` pour pointer vers la nouvelle structure de répertoires.

### Corrigé
- **Imports et sys.path** : Correction groupée de tous les scripts CLI pour garantir la résolution des imports malgré la profondeur de répertoire accrue.

## [0.6.0] - 2026-03-08

### Ajouté
- **Nouveau Menu Interactif (TUI)** : Interface textuelle riche remplaçant l'ancien wrapper Bash/fzf.
  - Double panneau dynamique : Navigation à gauche, Aide/Options à droite.
  - Coloration ANSI intégrée dans le panneau d'aide.
  - Raccourcis clavier : `[h]` pour l'aide, `[o]` pour les options, `[Enter]` pour lancer, `[q]` pour quitter.
  - Analyse dynamique des scripts CLI : Détecte automatiquement les arguments obligatoires et optionnels.
  - Configuration externalisée dans `src/git_ia_assistant/config/ia_menu.yaml`.
- **Améliorations de la Librairie Commune (`python_commun`)** :
  - `menu_utils.py` : Nouveau module pour l'analyse sécurisée des docstrings sans import.
  - `git_core.py` : `pousser_vers_distant` répare désormais automatiquement l'état "HEAD détachée" (fusion automatique sur master/main).
  - `git_core.py` : Filtrage intelligent des fichiers ignorés par Git (via `.gitignore`) dans la liste des modifications détectées.
  - `usage.py` : Export de la fonction `colorier_aide` pour réutilisation dans les interfaces TUI.

### Amélioré
- **Standardisation des Docstrings** : Mise à jour de tous les scripts CLI pour inclure le tag `(OBLIGATOIRE)` facilitant le parsing dynamique.
- **Workflow de Commit** : La classe de base `IaAssistantCommit` filtre désormais les fichiers ignorés par Git avant de tenter un `git add`, évitant les crashs silencieux.
- **Script d'installation** : `install.sh` configure désormais l'alias `ia` pointant directement sur le nouveau menu Python.

### Corrigé
- Correction d'un bug d'importation dans `usage.py` qui affectait tous les outils CLI.
- Correction des chemins système dans le menu interactif pour une résolution d'imports fiable depuis n'importe quel emplacement.

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
