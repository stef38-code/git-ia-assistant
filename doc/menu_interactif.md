# Utilisation du menu interactif `ia`

Après installation, un menu interactif professionnel `ia` est disponible pour piloter l'ensemble des outils :

```bash
ia
```

## ✨ Fonctionnalités avancées

- 📋 **Interface Double Panneau** : Navigation dans les outils à gauche, détails à droite.
- 👁️ **Aide Automatique** : L'aide colorée s'affiche instantanément lors de la navigation.
- ⚙️ **Structure des Paramètres** : Appuyez sur `[o]` pour voir les options obligatoires et facultatives.
- ⌨️ **Raccourcis Clavier** : 
  - `↑/↓` : Naviguer
  - `[h]` : Afficher l'aide (NAME + DESCRIPTION)
  - `[o]` : Afficher la structure des options
  - `Enter` : Valider et configurer les arguments
  - `[q]` ou `Ctrl-C` : Quitter proprement

## 📋 Commandes disponibles via le menu

*   `git-ia-commit` - Génération de commits
*   `git-ia-commit-version` - Versioning automatique
*   `git-ia-review` - Revue de code locale
*   `git-ia-mr` - Revue de MR/PR
*   `git-ia-squash` - Stratégie de squash
*   `git-ia-changelog` - Génération de changelog
*   `git-ia-explain` - Explication de code
*   `git-ia-test` - Génération de tests
*   `git-ia-doc` - Documentation automatique
*   `git-ia-refacto` - Suggestions de refactoring

## ⌨️ Utilisation directe

Si vous connaissez déjà la commande et souhaitez passer outre le menu :
```bash
ia git-ia-commit --help
ia git-ia-review mon_fichier.py
```
