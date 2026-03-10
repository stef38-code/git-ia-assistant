# Guide d'utilisation détaillé

Chaque outil est disponible sous forme de commande CLI. Par défaut, les outils tentent de détecter l'IA disponible, mais vous pouvez forcer un choix avec l'option `--ia` ou `-ia`.

## 📝 Génération de Commits
Analyse les fichiers modifiés et propose un message de commit.
```bash
git-ia-commit                   # Utilise l'IA par défaut
git-ia-commit --ia gemini       # Force l'utilisation de Gemini
git-ia-commit --dry-run         # Affiche uniquement le diff qui serait envoyé
git-ia-commit --optimise        # Propose des regroupements de commits
git-ia-commit --optimise --partiel # Permet de découper un fichier en plusieurs commits
git-ia-commit -f file1.py       # Analyse uniquement des fichiers spécifiques
git-ia-commit-version           # Commit + versioning automatique + CHANGELOG
```

## 🔍 Revue de Code locale
Analyse vos modifications locales pour suggérer des améliorations.
```bash
git-ia-review                   # Analyse tous les fichiers modifiés
git-ia-review -ia ollama        # Utilise Ollama pour la revue
git-ia-review fichier.py        # Revue d'un fichier spécifique
```

## 🚀 Revue de MR/PR
Réalise une revue complète d'une Merge Request GitLab ou Pull Request GitHub.

```bash
# GitLab - Revue d'une Merge Request
git-ia-mr -u https://gitlab.com/org/repo/-/merge_requests/45

# GitHub - Revue d'une Pull Request  
git-ia-mr -u https://github.com/user/repo/pull/123

# Publier automatiquement le rapport dans la MR/PR
git-ia-mr -u https://gitlab.com/org/repo/-/merge_requests/45 --publier

# Forcer une IA spécifique
git-ia-mr -u https://github.com/user/repo/pull/123 --ia gemini

# Mode dry-run (affiche le prompt sans appeler l'IA)
git-ia-mr -u https://gitlab.com/org/repo/-/merge_requests/45 --dry-run
```

**Sortie** : Le script génère plusieurs fichiers dans `~/ia_assistant/mrOrpr/` :
- `mrOrpr_<projet>_<numero>.md` : Rapport final de revue avec analyse IA.
- `prompt_genere_mr<numero>.md` : Prompt envoyé à l'IA (pour debug).

**Fonctionnalités avancées** :
- 🔄 Détection automatique de migration (Python, Java, Node.js, Angular, React)
- 📊 Protection contre les MR volumineuses (avec suggestions)
- 📤 Publication optionnelle du rapport comme commentaire dans la MR/PR

## 📚 Documentation
Génère de la documentation pour un fichier source.
```bash
git-ia-doc mon_code.py          # Génère des docstrings Python
git-ia-doc Service.java -f Javadoc -l English
```

## 💡 Explication de Code
Obtenez une explication détaillée d'un fichier complexe.
```bash
git-ia-explain script_complexe.py
```

## 🧪 Génération de Tests
Crée des tests unitaires pour vos fichiers.
```bash
git-ia-test composant.ts --framework Vitest
git-ia-test service.py --type unit
```

## 🛠️ Refactorisation
Propose une version modernisée de votre code.
```bash
git-ia-refacto vieux_script.py --version 3.12
```

## 📜 Changelog & Squash
Gérez votre historique Git.
```bash
git-ia-changelog -c 20          # Génère un changelog sur les 20 derniers commits
git-ia-squash --commits 10      # Suggère des regroupements sur les 10 derniers commits
```
