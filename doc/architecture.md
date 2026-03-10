# Structure du projet et Architecture

L'architecture est conçue pour être modulaire, permettant l'ajout facile de nouveaux fournisseurs d'IA ou de nouvelles fonctionnalités.

## 🧱 Organisation des répertoires

*   **`src/git_ia_assistant/cli/`** : Points d'entrée pour chaque commande CLI.
*   **`src/git_ia_assistant/core/`** : Logique métier, orchestration et classes de base (Interfaces).
*   **`src/git_ia_assistant/ia/`** : Implémentations spécifiques pour chaque moteur d'IA (Copilot, Gemini, Ollama).
*   **`src/git_ia_assistant/prompts/`** : Templates de prompts Markdown organisés par thématique.
*   **`src/git_ia_assistant/config/`** : Fichiers de configuration (YAML).
*   **`libs/python_commun/`** : (Sous-module Git) Librairie partagée contenant les utilitaires transverses (Git, System, Logging).

## 🏗️ Principes de conception

- **Pattern Factory** : Les fonctionnalités utilisent des factories pour instancier dynamiquement le bon fournisseur d'IA.
- **Séparation des préoccupations** : Les prompts sont isolés du code logique dans des fichiers Markdown.
- **Réutilisabilité** : Utilisation intensive de la librairie `python_commun` pour garantir la cohérence entre les outils.
