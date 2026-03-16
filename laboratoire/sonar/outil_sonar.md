
## 📋 Vue d'ensemble


## 🎯 Objectif

Créer un outil CLI qui :
2. Récupère les métriques de qualité pour un projet donné
3. Affiche un rapport structuré des problèmes détectés
4. Permet le filtrage par sévérité et type
5. Génère des rapports exportables (JSON, Markdown)

## 🔐 Prérequis

### Variables d'environnement requises

```bash
export SONAR_HOST_URL="https://sonarcloud.io"
# export SONAR_HOST_URL="https://sonar.example.com"

export SONAR_TOKEN="votre_token_ici"
#     ou: sqp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx (SonarCloud)

# Clé du projet à analyser
export SONAR_PROJECT_KEY="mon-organisation_mon-projet"
```


2. Mon compte → Sécurité → Tokens
3. Générer un nouveau token avec le scope "Execute Analysis"

**SonarCloud** :
1. Se connecter à https://sonarcloud.io
2. Mon compte → Security → Generate Tokens
3. Générer un token avec les droits "Browse"


### 1. Récupération des métriques globales

**Endpoint** : `/api/measures/component`

**Méthode** : `GET`

**Paramètres** :
- `component` : Clé du projet
- `metricKeys` : Métriques à récupérer (séparées par des virgules)

**Métriques disponibles** :
- `bugs` : Nombre de bugs
- `vulnerabilities` : Nombre de vulnérabilités
- `code_smells` : Nombre de code smells
- `security_hotspots` : Nombre de hotspots de sécurité
- `coverage` : Couverture de code (%)
- `duplicated_lines_density` : Taux de duplication (%)
- `ncloc` : Nombre de lignes de code (hors commentaires)
- `sqale_index` : Dette technique (minutes)
- `reliability_rating` : Note de fiabilité (A-E)
- `security_rating` : Note de sécurité (A-E)
- `sqale_rating` : Note de maintenabilité (A-E)

**Exemple de requête** :
```bash
curl -u "${SONAR_TOKEN}:" \
  "${SONAR_HOST_URL}/api/measures/component?component=${SONAR_PROJECT_KEY}&metricKeys=bugs,vulnerabilities,code_smells,security_hotspots,coverage,ncloc"
```

**Réponse (JSON)** :
```json
{
  "component": {
    "key": "mon-projet",
    "name": "Mon Projet",
    "qualifier": "TRK",
    "measures": [
      {"metric": "bugs", "value": "12"},
      {"metric": "vulnerabilities", "value": "3"},
      {"metric": "code_smells", "value": "45"},
      {"metric": "security_hotspots", "value": "2"},
      {"metric": "coverage", "value": "78.5"},
      {"metric": "ncloc", "value": "15234"}
    ]
  }
}
```

### 2. Récupération des issues détaillées

**Endpoint** : `/api/issues/search`

**Méthode** : `GET`

**Paramètres** :
- `componentKeys` : Clé du projet
- `types` : Type d'issues (BUG, VULNERABILITY, CODE_SMELL, SECURITY_HOTSPOT)
- `severities` : Sévérité (BLOCKER, CRITICAL, MAJOR, MINOR, INFO)
- `resolved` : Filtrer par statut (false = ouvert uniquement)
- `ps` : Page size (max 500)
- `p` : Numéro de page

**Exemple de requête** :
```bash
# Récupérer toutes les vulnérabilités non résolues
curl -u "${SONAR_TOKEN}:" \
  "${SONAR_HOST_URL}/api/issues/search?componentKeys=${SONAR_PROJECT_KEY}&types=VULNERABILITY&resolved=false&ps=500"

# Récupérer tous les bugs critiques
curl -u "${SONAR_TOKEN}:" \
  "${SONAR_HOST_URL}/api/issues/search?componentKeys=${SONAR_PROJECT_KEY}&types=BUG&severities=BLOCKER,CRITICAL&resolved=false&ps=500"
```

**Réponse (JSON)** :
```json
{
  "total": 12,
  "p": 1,
  "ps": 500,
  "paging": {
    "pageIndex": 1,
    "pageSize": 500,
    "total": 12
  },
  "issues": [
    {
      "key": "AX1234567890",
      "rule": "java:S2259",
      "severity": "MAJOR",
      "component": "mon-projet:src/main/java/com/example/Service.java",
      "line": 42,
      "message": "NullPointerException might be thrown as 'user' is nullable here",
      "type": "BUG",
      "status": "OPEN",
      "effort": "5min",
      "debt": "5min",
      "tags": ["cert", "cwe"]
    }
  ]
}
```

### 3. Récupération des hotspots de sécurité

**Endpoint** : `/api/hotspots/search`

**Méthode** : `GET`

**Paramètres** :
- `projectKey` : Clé du projet
- `status` : Statut (TO_REVIEW, REVIEWED)
- `resolution` : Résolution (SAFE, FIXED, ACKNOWLEDGED)

**Exemple de requête** :
```bash
curl -u "${SONAR_TOKEN}:" \
  "${SONAR_HOST_URL}/api/hotspots/search?projectKey=${SONAR_PROJECT_KEY}&status=TO_REVIEW"
```

## 🛠️ Implémentation Python

### Structure du script

```python
#!/usr/bin/env python3
"""

Ce script récupère les métriques de qualité (bugs, vulnérabilités, code smells)

Variables d'environnement requises :
- SONAR_TOKEN : Token d'authentification
- SONAR_PROJECT_KEY : Clé du projet à analyser
"""
```

### Fonctionnalités à implémenter

#### 1. **Connexion et authentification**
```python
import os
import requests
from typing import Dict, List, Optional

    def __init__(self):
        self.host_url = os.getenv("SONAR_HOST_URL")
        self.token = os.getenv("SONAR_TOKEN")
        self.project_key = os.getenv("SONAR_PROJECT_KEY")
        
        if not all([self.host_url, self.token, self.project_key]):
            raise ValueError("Variables d'environnement manquantes")
        
        self.session = requests.Session()
        self.session.auth = (self.token, "")  # Token comme username, password vide
    
    def _get(self, endpoint: str, params: Dict) -> Dict:
        url = f"{self.host_url}{endpoint}"
        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
```

#### 2. **Récupération des métriques globales**
```python
def get_project_metrics(self) -> Dict:
    """Récupère les métriques globales du projet."""
    metrics = [
        "bugs", "vulnerabilities", "code_smells", "security_hotspots",
        "coverage", "ncloc", "duplicated_lines_density",
        "reliability_rating", "security_rating", "sqale_rating",
        "sqale_index"
    ]
    
    params = {
        "component": self.project_key,
        "metricKeys": ",".join(metrics)
    }
    
    data = self._get("/api/measures/component", params)
    
    # Formatter les résultats
    measures = {}
    for measure in data.get("component", {}).get("measures", []):
        measures[measure["metric"]] = measure.get("value", "0")
    
    return measures
```

#### 3. **Récupération des issues détaillées**
```python
def get_issues(self, issue_type: str = None, severity: str = None) -> List[Dict]:
    """
    Récupère les issues du projet.
    
    Args:
        issue_type: BUG, VULNERABILITY, CODE_SMELL, SECURITY_HOTSPOT
        severity: BLOCKER, CRITICAL, MAJOR, MINOR, INFO
    """
    params = {
        "componentKeys": self.project_key,
        "resolved": "false",
        "ps": 500,  # Page size
        "p": 1      # Page number
    }
    
    if issue_type:
        params["types"] = issue_type
    if severity:
        params["severities"] = severity
    
    all_issues = []
    while True:
        data = self._get("/api/issues/search", params)
        all_issues.extend(data.get("issues", []))
        
        # Pagination
        paging = data.get("paging", {})
        if paging.get("pageIndex", 1) * paging.get("pageSize", 500) >= paging.get("total", 0):
            break
        params["p"] += 1
    
    return all_issues
```

#### 4. **Génération de rapport**
```python
def generate_report(self) -> str:
    """Génère un rapport Markdown des résultats."""
    metrics = self.get_project_metrics()
    
    report += f"**Serveur** : {self.host_url}\n\n"
    
    # Métriques globales
    report += "## 📈 Métriques globales\n\n"
    report += f"- **Lignes de code** : {metrics.get('ncloc', 'N/A')}\n"
    report += f"- **Couverture de tests** : {metrics.get('coverage', 'N/A')}%\n"
    report += f"- **Duplication** : {metrics.get('duplicated_lines_density', 'N/A')}%\n"
    report += f"- **Dette technique** : {int(metrics.get('sqale_index', 0)) // 60}h {int(metrics.get('sqale_index', 0)) % 60}min\n\n"
    
    # Problèmes par type
    report += "## 🐛 Problèmes détectés\n\n"
    report += f"| Type | Nombre | Sévérité |\n"
    report += f"|------|--------|----------|\n"
    report += f"| 🔴 Bugs | {metrics.get('bugs', '0')} | {self._rating_to_emoji(metrics.get('reliability_rating', 'A'))} |\n"
    report += f"| 🛡️ Vulnérabilités | {metrics.get('vulnerabilities', '0')} | {self._rating_to_emoji(metrics.get('security_rating', 'A'))} |\n"
    report += f"| 💩 Code Smells | {metrics.get('code_smells', '0')} | {self._rating_to_emoji(metrics.get('sqale_rating', 'A'))} |\n"
    report += f"| 🔥 Hotspots sécurité | {metrics.get('security_hotspots', '0')} | - |\n\n"
    
    # Top 10 des bugs critiques
    critical_bugs = self.get_issues(issue_type="BUG", severity="BLOCKER,CRITICAL")
    if critical_bugs:
        report += "## 🚨 Top 10 Bugs critiques\n\n"
        for i, issue in enumerate(critical_bugs[:10], 1):
            file_path = issue.get("component", "").split(":")[-1]
            line = issue.get("line", "?")
            message = issue.get("message", "")
            severity = issue.get("severity", "")
            report += f"{i}. **{severity}** - {file_path}:{line}\n"
            report += f"   > {message}\n\n"
    
    return report

def _rating_to_emoji(self, rating: str) -> str:
    ratings = {"A": "🟢", "B": "🟡", "C": "🟠", "D": "🔴", "E": "🔴"}
    return ratings.get(rating, "⚪")
```

#### 5. **Export JSON**
```python
import json

def export_json(self, output_file: str):
    """Exporte les données en JSON."""
    data = {
        "project_key": self.project_key,
        "metrics": self.get_project_metrics(),
        "bugs": self.get_issues(issue_type="BUG"),
        "vulnerabilities": self.get_issues(issue_type="VULNERABILITY"),
        "code_smells": self.get_issues(issue_type="CODE_SMELL")
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
```

## 🎨 Interface CLI

### Options proposées

```bash
# Afficher le rapport global
git-ia-sonar

# Filtrer par type de problème
git-ia-sonar --type bugs
git-ia-sonar --type vulnerabilities
git-ia-sonar --type code-smells

# Filtrer par sévérité
git-ia-sonar --severity critical
git-ia-sonar --severity blocker,critical

# Export en JSON
git-ia-sonar --export report.json

# Mode verbeux avec détails de chaque issue
git-ia-sonar --verbose

# Spécifier un projet différent
git-ia-sonar --project mon-autre-projet

# Mode dry-run (affiche les requêtes sans les exécuter)
git-ia-sonar --dry-run
```

### Parser d'arguments

```python
import argparse

def _parser_options() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        add_help=False
    )
    parser.add_argument("-h", "--help", action="store_true", help="Afficher l'aide")
    parser.add_argument("--dry-run", action="store_true", help="Simuler sans exécuter")
    parser.add_argument("--type", choices=["bugs", "vulnerabilities", "code-smells", "all"],
                       default="all", help="Type de problèmes à récupérer")
    parser.add_argument("--severity", help="Filtrer par sévérité (BLOCKER,CRITICAL,MAJOR,MINOR,INFO)")
    parser.add_argument("--export", metavar="FILE", help="Exporter en JSON")
    parser.add_argument("--project", help="Clé du projet (surcharge SONAR_PROJECT_KEY)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Mode verbeux")
    
    return parser.parse_args()
```

## 📊 Format de sortie

### Rapport console (par défaut)

```

Serveur : https://sonarcloud.io

📈 Métriques globales
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Lignes de code : 15,234
- Couverture de tests : 78.5%
- Duplication : 3.2%
- Dette technique : 12h 45min

🐛 Problèmes détectés
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
| Type               | Nombre | Note |
|--------------------|--------|------|
| 🔴 Bugs            |     12 | 🟢 A |
| 🛡️ Vulnérabilités  |      3 | 🟡 B |
| 💩 Code Smells     |     45 | 🟢 A |
| 🔥 Hotspots        |      2 | -    |

🚨 Top 10 Bugs critiques
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. CRITICAL - src/main/java/Service.java:42
   > NullPointerException might be thrown as 'user' is nullable here

2. CRITICAL - src/main/java/Controller.java:128
   > Resources should be closed

3. MAJOR - src/utils/Helper.java:67
   > Remove this unused private method
```

### Export JSON

```json
{
  "project_key": "mon-organisation_mon-projet",
  "server_url": "https://sonarcloud.io",
  "timestamp": "2026-03-06T15:30:00Z",
  "metrics": {
    "bugs": "12",
    "vulnerabilities": "3",
    "code_smells": "45",
    "security_hotspots": "2",
    "coverage": "78.5",
    "ncloc": "15234",
    "reliability_rating": "A",
    "security_rating": "B",
    "sqale_rating": "A"
  },
  "issues": {
    "bugs": [
      {
        "key": "AX123",
        "rule": "java:S2259",
        "severity": "CRITICAL",
        "file": "src/main/java/Service.java",
        "line": 42,
        "message": "NullPointerException might be thrown",
        "effort": "5min"
      }
    ],
    "vulnerabilities": [...],
    "code_smells": [...]
  }
}
```

## 🔄 Intégration avec git-ia-assistant

### Cas d'usage proposés

1. **Avant un commit** : Vérifier la qualité du code
   ```bash
   git-ia-sonar --severity blocker,critical
   # Si des problèmes critiques : demander confirmation avant commit
   ```

2. **Dans un hook pre-push** : Bloquer le push si qualité dégradée
   ```bash
   #!/bin/bash
   critical_bugs=$(git-ia-sonar --type bugs --severity blocker,critical --export /tmp/sonar.json | jq '.metrics.bugs')
   if [ "$critical_bugs" -gt 0 ]; then
       echo "❌ Push bloqué : $critical_bugs bugs critiques détectés"
       exit 1
   fi
   ```

3. **Génération de revue de code IA** : Enrichir le contexte
   ```bash
   git-ia-review mon-fichier.java
   ```

4. **Rapport périodique** : Générer un dashboard
   ```bash
   git-ia-sonar --export sonar-report-$(date +%Y%m%d).json
   # → Archiver les rapports pour suivi temporel
   ```

## 🚀 Étapes de développement

- [ ] Connexion à l'API avec authentification
- [ ] Récupération des métriques globales
- [ ] Affichage console simple

### Phase 2 : Récupération des issues
- [ ] Endpoint `/api/issues/search`
- [ ] Pagination automatique
- [ ] Filtrage par type et sévérité

### Phase 3 : Rapports enrichis
- [ ] Génération de rapport Markdown
- [ ] Export JSON
- [ ] Top 10 des problèmes critiques

### Phase 4 : Intégration git-ia-assistant
- [ ] Point d'entrée CLI `git-ia-sonar`
- [ ] Configuration via pyproject.toml
- [ ] Alias dans install.sh
- [ ] Documentation README

### Phase 5 : Fonctionnalités avancées
- [ ] Comparaison entre deux analyses (trend)
- [ ] Intégration dans git-ia-review (context enrichi)
- [ ] Génération de suggestions de fix via IA
- [ ] Dashboard HTML interactif

## 🔒 Sécurité

### Protection des secrets

❌ **NE JAMAIS** :
- Hardcoder le token dans le code
- Logger le token dans les sorties
- Commiter le token dans Git
- Afficher le token en clair

✅ **TOUJOURS** :
- Utiliser des variables d'environnement
- Masquer le token dans les logs (`SONAR_TOKEN=***`)
- Vérifier la présence du token avant exécution
- Documenter comment générer un token

### Validation des URLs

```python
def validate_url(url: str) -> bool:
    """Valide que l'URL est HTTPS."""
    if not url.startswith("https://"):
        logger.log_warning("L'URL doit utiliser HTTPS")
        return False
    return True
```

## 🤖 Intégration IA pour proposer des solutions

### Vue d'ensemble

1. Une explication détaillée du problème
2. Les risques associés
3. Des suggestions de correction concrètes
4. Un exemple de code corrigé

### Workflow proposé

```
                                       ↓
                            Chargement du fichier concerné
                                       ↓
                            Extraction du contexte (±10 lignes)
                                       ↓
                            Génération du prompt IA
                                       ↓
                            Envoi au fournisseur IA
                                       ↓
                            Réception des suggestions
                                       ↓
                            Affichage formaté
```

### Templates de prompts

#### 1. Prompt pour les Bugs

**Fichier** : `src/git_ia_assistant/prompts/sonar/bug_fix_prompt.md`

```markdown


## 📋 Informations du bug

**Sévérité** : {severity}
**Fichier** : {file_path}
**Ligne** : {line}

## 📝 Code concerné

**Langage** : {language}

```{language}
{code_context}
```

**Ligne problématique** : Ligne {line}
```{language}
{problematic_line}
```

## 🎯 Ta mission

1. **Analyse du bug** :
   - Explique pourquoi ce code est considéré comme un bug
   - Décris les risques potentiels (crash, données incorrectes, comportement imprévu)
   - Identifie les scénarios où le bug se manifeste

2. **Impact** :
   - Liste les conséquences possibles en production
   - Indique si le bug peut causer des pertes de données ou des failles de sécurité

3. **Solution recommandée** :
   - Propose une correction précise et minimale
   - Fournis le code corrigé complet (pas seulement la ligne modifiée)
   - Explique pourquoi cette correction résout le problème
   - Suggère des tests unitaires pour éviter la régression

4. **Bonnes pratiques** :
   - Recommande des patterns à adopter pour éviter ce type de bug
   - Suggère des outils de détection complémentaires (linters, types)

## 📊 Format de réponse attendu

### 🔍 Analyse
[Explication du bug]

### ⚠️ Risques
- Risque 1
- Risque 2

### ✅ Solution
```{language}
[Code corrigé complet]
```

### 📝 Explication de la correction
[Pourquoi cette correction fonctionne]

### 🧪 Tests recommandés
```{language}
[Exemple de test unitaire]
```

### 💡 Bonnes pratiques
- Pratique 1
- Pratique 2
```

#### 2. Prompt pour les Vulnérabilités

**Fichier** : `src/git_ia_assistant/prompts/sonar/vulnerability_fix_prompt.md`

```markdown


## 🔒 Informations de la vulnérabilité

**Sévérité** : {severity}
**Fichier** : {file_path}
**Ligne** : {line}
**Tags** : {tags}

## 📝 Code vulnérable

**Langage** : {language}

```{language}
{code_context}
```

**Ligne vulnérable** : Ligne {line}
```{language}
{problematic_line}
```

## 🎯 Ta mission

1. **Analyse de la vulnérabilité** :
   - Identifie le type de vulnérabilité (injection SQL, XSS, CSRF, etc.)
   - Référence OWASP Top 10 ou CWE si applicable
   - Explique comment un attaquant pourrait exploiter cette faille
   - Évalue le vecteur d'attaque et l'impact potentiel

2. **Démonstration d'exploitation** (si pertinent) :
   - Fournis un exemple d'attaque (sans code malveillant exécutable)
   - Montre les données qui pourraient être compromises
   - Explique la chaîne d'exploitation

3. **Correction sécurisée** :
   - Propose une correction qui élimine complètement la vulnérabilité
   - Utilise les bonnes pratiques de sécurité (validation, sanitisation, encoding)
   - Fournis le code corrigé avec commentaires de sécurité
   - Vérifie qu'aucune nouvelle vulnérabilité n'est introduite

4. **Défense en profondeur** :
   - Suggère des mesures de sécurité additionnelles (WAF, CSP, rate limiting)
   - Recommande des contrôles de sécurité au niveau architecture
   - Propose des audits de sécurité complémentaires

## 📊 Format de réponse attendu

### 🔍 Analyse de la vulnérabilité
**Type** : [Type OWASP/CWE]
**Vecteur d'attaque** : [Comment exploiter]
**Impact** : [Conséquences]

### 💣 Scénario d'exploitation
[Description de l'attaque sans code malveillant]

### ✅ Solution sécurisée
```{language}
[Code corrigé avec sécurité renforcée]
```

### 🛡️ Explication de la correction
[Pourquoi cette correction élimine la vulnérabilité]

### 🧪 Tests de sécurité recommandés
```{language}
[Tests de non-régression de sécurité]
```

### 🔐 Mesures complémentaires
- Mesure 1 (niveau applicatif)
- Mesure 2 (niveau infrastructure)
- Mesure 3 (niveau monitoring)

### 📚 Références
- OWASP : [Lien]
- CWE : [Lien]
```

#### 3. Prompt pour les Code Smells

**Fichier** : `src/git_ia_assistant/prompts/sonar/code_smell_fix_prompt.md`

```markdown


## 📋 Informations du code smell

**Sévérité** : {severity}
**Fichier** : {file_path}
**Ligne** : {line}
**Dette technique** : {debt}

## 📝 Code concerné

**Langage** : {language}

```{language}
{code_context}
```

**Ligne problématique** : Ligne {line}
```{language}
{problematic_line}
```

## 🎯 Ta mission

1. **Analyse du code smell** :
   - Explique pourquoi ce code est considéré comme une mauvaise pratique
   - Identifie les principes SOLID ou Clean Code violés
   - Décris l'impact sur la maintenabilité et la lisibilité
   - Évalue la dette technique réelle (correspond-elle à {debt} ?)

2. **Impact sur le projet** :
   - Difficulté de maintenance (ajout de fonctionnalités, debugging)
   - Risque de bugs futurs
   - Complexité cognitive pour les développeurs
   - Performance (si applicable)

3. **Refactoring recommandé** :
   - Propose une ou plusieurs solutions de refactoring
   - Fournis le code refactoré complet
   - Utilise les patterns de conception appropriés
   - Assure que la fonctionnalité reste identique

4. **Validation du refactoring** :
   - Vérifie que le code respecte les principes Clean Code
   - Confirme que la complexité cyclomatique est réduite
   - Suggère des tests pour garantir la non-régression
   - Compare avant/après (lisibilité, maintenabilité)

## 📊 Format de réponse attendu

### 🔍 Analyse du code smell
**Principe violé** : [SOLID/Clean Code]
**Impact maintenabilité** : [Description]
**Complexité** : [Estimation]

### 📉 Problèmes identifiés
- Problème 1
- Problème 2

### ✅ Code refactoré
```{language}
[Code refactoré complet]
```

### 📝 Explication du refactoring
**Changements effectués** :
- Changement 1
- Changement 2

**Bénéfices** :
- Bénéfice 1
- Bénéfice 2

### 🧪 Tests de non-régression
```{language}
[Tests pour valider le refactoring]
```

### 💡 Bonnes pratiques appliquées
- Pratique 1 (ex: Single Responsibility Principle)
- Pratique 2 (ex: Don't Repeat Yourself)
```

### Implémentation dans le code Python

#### Classe pour générer les suggestions IA

```python
from typing import Dict, List
from python_commun.ai.prompt import charger_prompt, formatter_prompt
from python_commun.logging import logger

class SonarIssueAIAnalyzer:
    
    def __init__(self, ia_provider: str = "copilot"):
        """
        Args:
            ia_provider: Fournisseur IA (copilot, gemini, ollama)
        """
        self.ia_provider = ia_provider
        self._load_prompts()
    
    def _load_prompts(self):
        """Charge les templates de prompts."""
        self.prompts = {
            "BUG": charger_prompt("sonar/bug_fix_prompt.md"),
            "VULNERABILITY": charger_prompt("sonar/vulnerability_fix_prompt.md"),
            "CODE_SMELL": charger_prompt("sonar/code_smell_fix_prompt.md")
        }
    
    def analyze_issue(self, issue: Dict, file_content: str) -> Dict:
        """
        
        Args:
            file_content: Contenu complet du fichier
        
        Returns:
            Dict avec analyse, solution, tests, bonnes pratiques
        """
        issue_type = issue.get("type", "CODE_SMELL")
        
        # Extraire le contexte du code (±10 lignes autour du problème)
        context = self._extract_code_context(
            file_content, 
            issue.get("line", 1),
            context_lines=10
        )
        
        # Préparer les données du prompt
        prompt_data = {
            "rule_key": issue.get("rule", "unknown"),
            "severity": issue.get("severity", "MAJOR"),
            "file_path": issue.get("component", "").split(":")[-1],
            "line": issue.get("line", "?"),
            "message": issue.get("message", ""),
            "tags": ", ".join(issue.get("tags", [])),
            "debt": issue.get("debt", "5min"),
            "language": self._detect_language(issue.get("component", "")),
            "code_context": context["full_context"],
            "problematic_line": context["problematic_line"]
        }
        
        # Formatter le prompt
        prompt_template = self.prompts.get(issue_type, self.prompts["CODE_SMELL"])
        prompt = formatter_prompt(prompt_template, **prompt_data)
        
        # Envoyer au fournisseur IA
        logger.log_info(f"Analyse de {issue_type} avec {self.ia_provider}...")
        response = self._send_to_ia(prompt)
        
        return {
            "issue_key": issue.get("key"),
            "issue_type": issue_type,
            "severity": issue.get("severity"),
            "file": prompt_data["file_path"],
            "line": prompt_data["line"],
            "ai_analysis": response
        }
    
    def _extract_code_context(self, file_content: str, line: int, context_lines: int = 10) -> Dict:
        """Extrait le contexte autour d'une ligne de code."""
        lines = file_content.split('\n')
        
        # Index (line est 1-based, list est 0-based)
        line_idx = line - 1
        
        # Limites du contexte
        start = max(0, line_idx - context_lines)
        end = min(len(lines), line_idx + context_lines + 1)
        
        # Contexte avec numéros de lignes
        context_lines_list = []
        for i in range(start, end):
            marker = ">>> " if i == line_idx else "    "
            context_lines_list.append(f"{marker}{i+1:4d} | {lines[i]}")
        
        return {
            "full_context": "\n".join(context_lines_list),
            "problematic_line": lines[line_idx] if line_idx < len(lines) else ""
        }
    
    def _detect_language(self, component: str) -> str:
        """Détecte le langage depuis le chemin du fichier."""
        extension_map = {
            ".java": "java",
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".go": "go",
            ".rs": "rust",
            ".cpp": "cpp",
            ".c": "c",
            ".cs": "csharp",
            ".rb": "ruby",
            ".php": "php"
        }
        
        for ext, lang in extension_map.items():
            if component.endswith(ext):
                return lang
        
        return "text"
    
    def _send_to_ia(self, prompt: str) -> str:
        """Envoie le prompt au fournisseur IA."""
        if self.ia_provider == "copilot":
            from python_commun.ai.copilot import envoyer_prompt_copilot
            return envoyer_prompt_copilot(prompt)
        elif self.ia_provider == "gemini":
            from python_commun.ai.gemini_utils import envoyer_prompt_gemini
            return envoyer_prompt_gemini(prompt)
        elif self.ia_provider == "ollama":
            from python_commun.ai.ollama_utils import appeler_ollama
            return appeler_ollama(prompt)
        else:
            raise ValueError(f"Fournisseur IA inconnu : {self.ia_provider}")
```


```python
    # ... (code existant)
    
    def analyze_issues_with_ai(self, issue_type: str = None, max_issues: int = 10) -> List[Dict]:
        """
        Récupère les issues et génère des suggestions IA.
        
        Args:
            issue_type: BUG, VULNERABILITY, CODE_SMELL
            max_issues: Nombre maximum d'issues à analyser
        
        Returns:
            Liste des analyses avec suggestions IA
        """
        issues = self.get_issues(issue_type=issue_type, severity="BLOCKER,CRITICAL")
        
        # Limiter le nombre d'issues (éviter les coûts IA excessifs)
        issues_to_analyze = issues[:max_issues]
        
        logger.log_info(f"Analyse de {len(issues_to_analyze)} issues avec IA...")
        
        # Créer l'analyzer IA
        analyzer = SonarIssueAIAnalyzer(ia_provider=os.getenv("IA_SELECTED", "copilot"))
        
        results = []
        for i, issue in enumerate(issues_to_analyze, 1):
            logger.log_info(f"[{i}/{len(issues_to_analyze)}] {issue.get('type')} - {issue.get('component')}")
            
            # Récupérer le contenu du fichier
            file_path = self._get_local_file_path(issue.get("component"))
            
            if not file_path or not os.path.exists(file_path):
                logger.log_warning(f"Fichier introuvable : {file_path}")
                continue
            
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            # Analyser avec IA
            analysis = analyzer.analyze_issue(issue, file_content)
            results.append(analysis)
        
        return results
    
    def _get_local_file_path(self, component: str) -> str:
        """
        
        Args:
            component: "project_key:src/main/java/Service.java"
        
        Returns:
            Chemin local : "src/main/java/Service.java"
        """
        # Extraire le chemin après le ":"
        if ":" in component:
            return component.split(":", 1)[1]
        return component
```

### Options CLI étendues

```bash
# Analyser les bugs avec suggestions IA
git-ia-sonar --type bugs --ai-suggestions

# Analyser les vulnérabilités critiques avec IA
git-ia-sonar --type vulnerabilities --severity blocker,critical --ai-suggestions

# Limiter le nombre d'analyses IA (coûts)
git-ia-sonar --ai-suggestions --max-ai-analysis 5

# Choisir le fournisseur IA
git-ia-sonar --ai-suggestions --ia gemini

# Export des suggestions en JSON
git-ia-sonar --ai-suggestions --export sonar-ai-report.json

# Mode interactif : appliquer les corrections proposées
git-ia-sonar --ai-suggestions --interactive
```

### Format de sortie avec suggestions IA

```

🐛 Bug #1 - CRITICAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 Fichier : src/main/java/Service.java:42
📏 Règle : java:S2259 (NullPointerException)
💬 Message : "user" is nullable here

🤖 Analyse IA (Copilot)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 Le code ne vérifie pas si 'user' est null avant d'accéder à ses propriétés.
   Cela peut provoquer une NullPointerException si la méthode getUser() retourne null.

⚠️ Risques :
   - Crash de l'application en production
   - Perte de données utilisateur en cours de traitement
   - Log d'erreur non informatif

✅ Solution recommandée :
```java
public void processUser(Long userId) {
    User user = userRepository.getUser(userId);
    
    // ✅ Vérification null avant utilisation
    if (user == null) {
        logger.warn("User not found: {}", userId);
        throw new UserNotFoundException(userId);
    }
    
    // Safe to use user now
    String email = user.getEmail();
    sendNotification(email);
}
```

📝 Explication : La vérification null explicite empêche le NPE et permet une gestion
   d'erreur appropriée avec un message clair.

🧪 Test recommandé :
```java
@Test
void testProcessUser_whenUserNotFound_shouldThrowException() {
    when(userRepository.getUser(999L)).thenReturn(null);
    
    assertThrows(UserNotFoundException.class, 
        () -> service.processUser(999L));
}
```

💡 Bonnes pratiques :
   - Utiliser Optional<User> pour signaler la possibilité de null
   - Ajouter des annotations @NonNull/@Nullable
   - Activer les null-safety warnings du compilateur

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 Appliquer cette correction ? [y: oui, n: non, e: éditer] :
```

### Mise à jour du parser d'arguments

```python
def _parser_options() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        add_help=False
    )
    # ... (options existantes)
    
    # Nouvelles options IA
    parser.add_argument("--ai-suggestions", action="store_true",
                       help="Générer des suggestions de correction via IA")
    parser.add_argument("--max-ai-analysis", type=int, default=10,
                       help="Nombre maximum d'issues à analyser avec IA (défaut: 10)")
    parser.add_argument("--ia", choices=["copilot", "gemini", "ollama"],
                       default="copilot", help="Fournisseur IA à utiliser")
    parser.add_argument("--interactive", action="store_true",
                       help="Mode interactif pour appliquer les corrections")
    
    return parser.parse_args()
```

### Workflow d'application automatique des corrections

```python
def apply_fix_interactively(analysis: Dict, file_path: str):
    """Applique une correction de manière interactive."""
    from InquirerPy import inquirer
    
    print(f"\n🔧 Correction proposée pour {file_path}:{analysis['line']}")
    print(analysis["ai_analysis"])
    
    choice = inquirer.select(
        message="Action à effectuer :",
        choices=[
            {"name": "✅ Appliquer la correction", "value": "apply"},
            {"name": "📝 Éditer avant d'appliquer", "value": "edit"},
            {"name": "⏭️  Ignorer", "value": "skip"},
            {"name": "🛑 Arrêter", "value": "stop"}
        ],
        default="apply"
    ).execute()
    
    if choice == "apply":
        # Extraire le code corrigé de l'analyse IA
        fixed_code = extract_code_from_ai_response(analysis["ai_analysis"])
        apply_fix_to_file(file_path, analysis["line"], fixed_code)
        logger.log_success(f"Correction appliquée à {file_path}")
        return "continue"
    
    elif choice == "edit":
        # Ouvrir l'éditeur pour permettre la modification
        edited_code = open_editor_with_suggestion(file_path, analysis["ai_analysis"])
        apply_fix_to_file(file_path, analysis["line"], edited_code)
        logger.log_success(f"Correction éditée et appliquée à {file_path}")
        return "continue"
    
    elif choice == "skip":
        logger.log_info("Correction ignorée")
        return "continue"
    
    else:  # stop
        return "stop"
```

## 📚 Ressources

- **SonarCloud API** : https://sonarcloud.io/web_api

## 💡 Exemple de configuration

```bash
# Fichier ~/.bashrc ou ~/.zshrc
export SONAR_HOST_URL="https://sonarcloud.io"
export SONAR_TOKEN="sqp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export SONAR_PROJECT_KEY="mon-organisation_git-ia-assistant"

# Alias pour faciliter l'usage
alias sonar-check="git-ia-sonar --severity blocker,critical"
alias sonar-report="git-ia-sonar --export /tmp/sonar-$(date +%Y%m%d).json"
```

## 🎯 Résumé

Ce scénario permet de :
2. ✅ Récupérer les bugs, vulnérabilités et code smells
3. ✅ **Générer des suggestions de correction via IA pour chaque problème**
4. ✅ **Proposer du code corrigé avec explications détaillées**
5. ✅ **Appliquer les corrections de manière interactive**
6. ✅ Générer des rapports exploitables
7. ✅ Intégrer dans les workflows Git
8. ✅ Protéger les informations sensibles via variables d'environnement

### Fonctionnalités IA ajoutées

- 📝 **3 templates de prompts spécialisés** (Bugs, Vulnérabilités, Code Smells)
- 🤖 **Analyse contextuelle** avec extraction du code environnant (±10 lignes)
- 💡 **Suggestions de correction** avec code avant/après
- 🧪 **Tests unitaires recommandés** pour chaque correction
- 🛡️ **Analyse de sécurité approfondie** pour les vulnérabilités (OWASP, CWE)
- 📚 **Bonnes pratiques** et patterns de conception recommandés
- 🔄 **Mode interactif** pour appliquer les corrections directement
- 🎛️ **Support multi-IA** (Copilot, Gemini, Ollama)

**Prochaine étape** : Implémenter le script Python dans `src/git_ia_assistant/cli/sonar_cli.py`
