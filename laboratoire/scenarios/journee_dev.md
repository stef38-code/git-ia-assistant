# Scénario : Journée Développeur (Algorithme)

Ce document détaille le flux de travail structuré d'un développeur utilisant les outils d'automatisation et d'IA du projet, structuré sous forme d'algorithme.

## 📜 Algorithme : Journée_Développeur

**DEBUT**

### 1. SÉLECTION : Choisir une carte dans JIRA (Statut: "To Do")
   - **Action** : Initialisation du ticket et récupération du contexte.
   - **Commande** : `script_init_task (ID_JIRA)`

### 2. PREPARATION : Clone/Pull du projet et création de branche
   - **Action** : Mise en place de l'environnement de travail local synchronisé avec JIRA.
   - **Commande** : `script_git_setup (ID_JIRA)`

### 3. DÉVELOPPEMENT :
   **TANT QUE** (Fonctionnalité non finie) **FAIRE** :
   - Coder (IDE)
   - **SI** (Besoin de design) : **EXECUTER** `script_figma_extract`
   - Tester localement
   **FIN TANT QUE**

### 4. QUALITÉ : Vérification avant envoi
   - **Action** : Analyse de la qualité de code via SonarCloud/SonarQube avec assistance IA.
   - **Commande** : `script_precheck_sonar`

### 5. LIVRAISON : Demande de relecture
   - **Action** : Création automatique de la Merge Request (MR/PR) avec résumé IA.
   - **Commande** : `script_create_mr`

**FIN**

---

## 🛠️ Scripts utilisés

| Etape | Script | Description |
|---|---|---|
| 1 | `script_init_task` | Connecte à JIRA, passe le ticket en "In Progress" et extrait la spec. |
| 2 | `script_git_setup` | Automatise `git checkout -b feature/ID_JIRA`, `git pull` et config de branche. |
| 3 | `script_figma_extract` | Récupère les assets ou specs CSS depuis un lien Figma via l'API Figma. |
| 4 | `script_precheck_sonar` | Lance un scan local ou interroge Sonar pour valider les Quality Gates. |
| 5 | `script_create_mr` | Pousse le code et ouvre la MR sur GitLab/GitHub via `git-ia-mr`. |

## 🔗 Intégration avec Git IA Assistant
Ce workflow s'appuie sur le moteur `git-ia-assistant` pour enrichir chaque étape (explication du ticket JIRA, génération de tests pendant le dév, revue Sonar assistée, etc.).
