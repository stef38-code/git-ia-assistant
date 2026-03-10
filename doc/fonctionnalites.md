# Fonctionnalités principales

Git IA Assistant offre un ensemble complet d'outils pour automatiser et enrichir vos interactions avec Git.

## 🚀 Workflow Git standard

*   **Génération de Commits** (`git-ia-commit`) : Analyse vos changements et génère un message conforme à *Conventional Commits*. 
    *   **Mode interactif** : Affinez le message avec des instructions supplémentaires.
    *   **Optimisation** (`--optimise`) : Regroupe intelligemment les fichiers en commits logiques.
    *   **Commits partiels** (`--partiel`) : Découpe un fichier en plusieurs commits via `git add -p`.
*   **Revue de Code** (`git-ia-review`) : Analyse vos fichiers locaux modifiés et propose des suggestions d'amélioration (lisibilité, bugs potentiels, bonnes pratiques). Supporte l'extraction de contexte pour les imports Python.
*   **Revue de MR/PR** (`git-ia-mr`) : Automatise la relecture des *Merge Requests* (GitLab) et *Pull Requests* (GitHub) en téléchargeant le diff et en générant un rapport complet incluant une **analyse de sécurité** et une **évaluation du risque**.
    *   **Détection de migration** : Identifie automatiquement les changements de version (Python, Java, Node.js, Angular, React)
    *   **Publication automatique** (`--publier`) : Publie le rapport directement comme commentaire dans la MR/PR
    *   **Protection volumétrique** : Analyse la taille et refuse les MR trop volumineuses avec suggestions
*   **Stratégie de Squash** (`git-ia-squash`) : Analyse votre historique récent pour suggérer quels commits fusionner lors d'un `git rebase -i`.
*   **Génération de Changelog** (`git-ia-changelog`) : Produit un fichier `CHANGELOG.md` structuré à partir de l'historique des commits.

## 💡 Nouveaux outils d'assistance

*   **Explication de Code** (`git-ia-explain`) : Explique de manière pédagogique et structurée un fichier ou une fonction complexe.
*   **Génération de Tests** (`git-ia-test`) : Génère des suites de tests unitaires ou E2E. Supporte **PyTest**, **JUnit 5**, **Jest/Jasmine**, **Vitest** et **Playwright**.
*   **Documentation Automatique** (`git-ia-doc`) : Génère de la documentation technique (Markdown, Javadoc, KDoc, Docstrings Python).
*   **Refactorisation Intelligente** (`git-ia-refacto`) : Propose des améliorations de code (lisibilité, performance, modularité) sans changer le comportement.
