# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
et ce projet adhère à [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
