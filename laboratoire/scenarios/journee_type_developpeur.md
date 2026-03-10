# Scénario : Journée type d'un développeur avec Git IA Assistant

Ce document décrit comment intégrer les outils de `git-ia-assistant` dans le flux de travail quotidien d'un développeur, en s'inspirant des meilleures pratiques d'assistance IA.

## 🌅 09:00 - Prise de connaissance et Analyse
Le développeur arrive et doit comprendre les changements récents sur le projet ou analyser un fichier complexe qu'il doit modifier.

- **Action** : Expliquer un fichier complexe ou un diff récent.
- **Outil** : `git-ia-explain`
- **Commande** :
  ```bash
  # Expliquer un fichier spécifique
  git-ia-explain src/core/logic.py
  
  # Expliquer les changements locaux (diff)
  git-ia-explain --diff
  ```

## 🛠️ 10:30 - Développement et Refactorisation
Pendant la phase de codage, le développeur souhaite améliorer la qualité de son code ou générer des tests unitaires.

- **Action** : Refactoriser du code pour la lisibilité ou générer des tests.
- **Outils** : `git-ia-refacto`, `git-ia-test`
- **Commandes** :
  ```bash
  # Proposer une refactorisation
  git-ia-refacto src/core/logic.py
  
  # Générer des tests unitaires pour une classe
  git-ia-test src/core/logic.py
  ```

## 🧪 14:00 - Revue de code locale
Avant de pousser ses changements, le développeur effectue une auto-revue assistée par l'IA pour détecter d'éventuels bugs ou oublis.

- **Action** : Lancer une revue de code sur les modifications locales.
- **Outil** : `git-ia-review`
- **Commande** :
  ```bash
  git-ia-review --staged
  ```

## 📝 16:00 - Commit et Versioning
Les changements sont prêts. Le développeur souhaite un message de commit clair et une gestion automatique de la version.

- **Action** : Créer un commit avec un message généré par l'IA et mettre à jour la version.
- **Outil** : `git-ia-commit-version`
- **Commande** :
  ```bash
  git-ia-commit-version --type feat --scope core
  ```

## 🚢 17:30 - Préparation de la Release
En fin de journée ou de sprint, le développeur génère le changelog pour documenter les nouveautés.

- **Action** : Générer le CHANGELOG.md basé sur les commits IA.
- **Outil** : `git-ia-changelog`
- **Commande** :
  ```bash
  git-ia-changelog --output CHANGELOG.md
  ```

---

## 🤖 Utilisation via le Menu Interactif
Toutes ces étapes peuvent être pilotées depuis le menu central :
```bash
ia
```
Puis naviguez avec les flèches pour sélectionner l'outil correspondant à votre étape de la journée.
