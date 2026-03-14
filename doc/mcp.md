# 🤖 Mode Agent (MCP)

La version 1.0.0 introduit le mode **Agent**, accessible via `git-ia-mr-mcp` et `git-ia-commit-mcp`. Contrairement au mode classique qui envoie tout le diff à l'IA, le mode Agent :
1.  **Configure un environnement sécurisé** avec vos serveurs MCP locaux.
2.  **Fournit des outils** à l'IA (lire un fichier, chercher un texte, voir le diff git).
3.  **Laisse l'IA décider** de ce qu'elle doit explorer pour comprendre votre code.

**Avantage :** Analyse beaucoup plus profonde des impacts, détection des régressions hors-diff et économie massive de tokens.

```bash
# Lancer une revue de MR en mode Agent
ia-mr-mcp -u https://gitlab.com/repo/-/merge_requests/123

# Générer un message de commit en mode Agent
ia-commit-mcp
```
