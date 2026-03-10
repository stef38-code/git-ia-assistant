# 📁 Organisation des Prompts Git IA Assistant

Ce répertoire contient **uniquement les templates de prompts Markdown** utilisés par Git IA Assistant pour interagir avec les différents fournisseurs d'IA (GitHub Copilot, Google Gemini, Ollama).

> **Note :** Les utilitaires Python pour la génération de prompts sont situés dans `src/git_ia_assistant/core/utils/`.

## 📂 Structure

Les prompts sont organisés en 4 catégories fonctionnelles :

### 🔄 commits/
Prompts liés à la gestion des commits Git.

- **commit_message_prompt.md** - Génération de messages de commit conformes à Conventional Commits v1.0.0
- **optimise_commit_prompt.md** - Optimisation et amélioration de commits existants
- **squash_prompt.md** - Fusion intelligente de commits multiples

**Commandes associées :** `git-ia-commit`, `git-ia-squash`

---

### 👁️ review/
Prompts pour la revue de code (code review) par langage.

- **python_review_prompt.md** - Revue de code Python (PEP 8, bonnes pratiques)
- **java_review_prompt.md** - Revue de code Java (conventions Oracle)
- **angular_review_prompt.md** - Revue de code Angular/TypeScript
- **mr_review_prompt.md** - Revue complète de Merge Request/Pull Request (multi-langage)

**Commandes associées :** `git-ia-review`, `git-ia-mr`

**Fonctionnalités :**
- Détection automatique du langage via `detect_lang_repo()`
- Suggestions de tests unitaires manquants
- Suggestions de tests de sécurité (OWASP Top 10)
- Format Given/When/Then pour les tests

---

### 🛠️ code_quality/
Prompts pour améliorer la qualité du code.

- **test_generation_prompt.md** - Génération de tests unitaires (PyTest, JUnit, Jest, Vitest, Playwright)
- **doc_generation_prompt.md** - Génération de documentation (docstrings, Javadoc, KDoc, JSDoc)
- **refacto_prompt.md** - Suggestions de refactoring pour améliorer le code existant

**Commandes associées :** `git-ia-test`, `git-ia-doc`, `git-ia-refacto`

---

### 📜 git_history/
Prompts pour analyser et documenter l'historique Git.

- **changelog_prompt.md** - Génération de CHANGELOG.md à partir des commits
- **explain_prompt.md** - Explication détaillée de l'historique Git d'une branche

**Commandes associées :** `git-ia-changelog`, `git-ia-explain`

---

## 🔧 Utilisation technique

### Chargement des prompts

Les prompts sont chargés via la fonction `charger_prompt()` de `python_commun.ai.prompt` :

```python
from python_commun.ai.prompt import charger_prompt, formatter_prompt

# Charger un prompt
template = charger_prompt("commits/commit_message_prompt.md", dossier_prompts)

# Formater avec des variables
prompt = formatter_prompt(template, diff=diff_text, langage="Python", branch_name="feature/xyz")
```

### Placeholders disponibles

Les prompts utilisent des placeholders qui sont remplacés dynamiquement :

#### Prompts commits/
- `{diff}` - Diff Git des changements
- `{langage}` - Langage du projet (Python, Java, Angular, etc.)
- `{branch_name}` - Nom de la branche Git
- `{version}` - Version du langage (optionnel)

#### Prompts review/
- `{code}` - Code source à analyser
- `{langage}` - Langage du projet
- `{version}` - Version du langage
- `{diff}` - Diff pour MR/PR
- `{url}` - URL de la MR/PR

#### Prompts code_quality/
- `{code}` - Code source
- `{fichier}` - Nom du fichier
- `{langage}` - Langage du projet
- `{version}` - Version du langage
- `{framework}` - Framework de test (PyTest, JUnit, etc.)

#### Prompts git_history/
- `{commits}` - Liste des commits Git
- `{branch}` - Nom de la branche
- `{diff}` - Diff des changements

### Package data (pyproject.toml)

Les prompts sont inclus dans la distribution du package via :

```toml
[tool.setuptools.package-data]
"git_ia_assistant" = [
    "prompts/*.md",
    "prompts/*.py",
    "prompts/commits/*.md",
    "prompts/review/*.md",
    "prompts/code_quality/*.md",
    "prompts/git_history/*.md"
]
```

---

## 📝 Conventions

### Format des prompts Markdown

Tous les prompts suivent une structure standardisée :

1. **Titre** - Description de la tâche
2. **Contexte** - Informations sur le projet/code
3. **Instructions** - Directives précises pour l'IA
4. **Format de sortie** - Structure attendue de la réponse
5. **Exemples** - Illustrations concrètes

### Règles de sécurité

⚠️ **IMPORTANT** : Les prompts ne doivent **JAMAIS** contenir :
- URLs internes d'entreprise
- Codes de projets privés
- Tokens/credentials
- Noms de personnes ou emails
- Adresses IP privées
- Chemins absolus spécifiques

### Langues

- **Prompts** : Rédigés en français
- **Code généré** : Suit les conventions du langage (anglais généralement)
- **Commentaires** : En français par défaut, paramétrable

---

## 🚀 Ajouter un nouveau prompt

Pour ajouter un nouveau prompt :

1. **Créer le fichier** dans le sous-répertoire approprié
   ```bash
   touch src/git_ia_assistant/prompts/<categorie>/<nom>_prompt.md
   ```

2. **Utiliser dans le code**
   ```python
   template = charger_prompt("<categorie>/<nom>_prompt.md", dossier_prompts)
   ```

3. **Ajouter au pyproject.toml** (si nouvelle catégorie)
   ```toml
   "prompts/<nouvelle_categorie>/*.md"
   ```

4. **Documenter** dans ce README

---

## 🔧 Utilitaires de génération de prompts

Les modules Python utilitaires pour la génération et le traitement des prompts sont situés dans `src/git_ia_assistant/core/utils/` :

### review_prompt.py

Module utilitaire pour charger dynamiquement les templates de revue de code selon le langage.

**Fonction principale :**
```python
from git_ia_assistant.core.utils.review_prompt import generate

prompt = generate(
    title="Titre de la MR",
    description="Description",
    files=["file1.py", "file2.py"],
    diff="diff content",
    author="user",
    language="Python",
    version="3.12"
)
```

**Fonctionnement :**
- Détecte automatiquement le template approprié : `prompts/review/{language}_review_prompt.md`
- Charge et formate le template avec les variables fournies
- Lève `FileNotFoundError` si le langage n'est pas supporté

---

## 📊 Statistiques

- **4 catégories** fonctionnelles
- **12 prompts** au total
- **9 commandes CLI** associées
- **3 fournisseurs IA** supportés (Copilot, Gemini, Ollama)
- **6 langages** supportés (Python, Java, Angular, TypeScript, JavaScript, Kotlin)

---

## 🔗 Références

- [Conventional Commits](https://www.conventionalcommits.org/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [PEP 8 - Style Guide for Python](https://peps.python.org/pep-0008/)
- [Google Java Style Guide](https://google.github.io/styleguide/javaguide.html)
- [Angular Style Guide](https://angular.io/guide/styleguide)

---

**Dernière mise à jour :** 2026-03-06  
**Version :** 0.2.1
