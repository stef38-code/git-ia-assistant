# 📊 Coverage & Test Assistant

> **Commande** : `git-ia-coverage`  
> **Statut** : 📝 En développement  
> **Priorité** : 🟡 Moyenne (Quick Win)  
> **Effort estimé** : 30 heures

---

## 📋 Vue d'ensemble

### Problème résolu

Les développeurs ont du mal à :
- Identifier rapidement les zones de code non testées
- Atteindre les seuils de couverture requis (80%, 90%)
- Générer des tests pour tous les edge cases

**Impact** : 2-3 heures par module pour atteindre une couverture acceptable.

### Solution proposée

`git-ia-coverage` analyse la couverture de code et **génère automatiquement** les tests manquants.

---

## 🎯 Fonctionnalités principales

### 1. Analyse de la couverture

```bash
# Détecte et affiche le rapport de couverture
git-ia-coverage analyze

# Avec seuil minimum
git-ia-coverage analyze --threshold 80  # Fail si < 80%

# Génère rapport HTML
git-ia-coverage analyze --report html --output coverage-report/
```

**Formats supportés** :
- **Java** : JaCoCo XML, Cobertura
- **Python** : coverage.xml (pytest-cov)
- **JavaScript/TypeScript** : Istanbul/NYC JSON, lcov
- **Angular** : Karma coverage

**Exemple de sortie** :
```
📊 Analyse de couverture terminée

Fichiers sous le seuil (80%) :
┌─────────────────────────────────┬──────────┬───────────┐
│ Fichier                         │ Coverage │ Manquants │
├─────────────────────────────────┼──────────┼───────────┤
│ src/UserService.java            │ 65%      │ 12 lignes │
│ src/OrderController.java        │ 72%      │ 8 lignes  │
│ src/utils/DateHelper.java       │ 45%      │ 20 lignes │
└─────────────────────────────────┴──────────┴───────────┘

💡 Suggestion IA :
   - UserService.java : manque tests pour cas d'erreur (null, exceptions)
   - DateHelper.java : aucun test pour formatage dates futures

Générer les tests manquants ? [y/n] : _
```

---

### 2. Affichage des zones non couvertes

```bash
# Liste fichiers sous un seuil
git-ia-coverage show --below 70

# Détails par fichier
git-ia-coverage show --file src/UserService.java

# Affiche les branches/lignes non couvertes
```

**Exemple de sortie** :
```
📄 src/UserService.java - Couverture : 65%

Lignes non couvertes :
  - Lines 45-52 : gestion exception NullPointerException
  - Line 78 : branche if (user.isAdmin())
  - Lines 92-95 : rollback transaction

Branches non couvertes :
  - if/else line 78 : branche else jamais testée
  - switch/case line 110 : case "INACTIVE" jamais testé

💡 IA suggère de tester :
   1. Cas où user est null (ligne 45)
   2. Cas où user.isAdmin() == true (ligne 78)
   3. Cas d'erreur lors du rollback (ligne 92)
```

---

### 3. Génération automatique de tests

```bash
# Génère tests pour atteindre un seuil
git-ia-coverage generate --file src/UserService.java --target 90

# Mode interactif
git-ia-coverage generate --interactive
```

**Processus** :
1. Analyse les branches/lignes non couvertes
2. Génère tests via IA pour chaque cas manquant
3. Demande confirmation avant création

**Exemple de génération** :

```
🧪 Génération de tests pour src/UserService.java

Test 1/3 - Cas d'erreur : user null
────────────────────────────────────────────────
@Test
void testFindUserById_NullUser() {
    // Arrange
    when(userRepository.findById(999L)).thenReturn(Optional.empty());
    
    // Act & Assert
    assertThrows(UserNotFoundException.class, () -> {
        userService.findUserById(999L);
    });
}
────────────────────────────────────────────────
Créer ce test ? [y: oui, n: non, e: éditer, a: créer tous] : y

✅ Test créé : src/test/java/.../UserServiceTest.java (ligne 45)

Test 2/3 - Branche admin : user.isAdmin() == true
────────────────────────────────────────────────
@Test
void testDeleteUser_AdminUser() {
    // Arrange
    User admin = new User(1L, "admin", "admin@example.com");
    admin.setRole(Role.ADMIN);
    when(userRepository.findById(1L)).thenReturn(Optional.of(admin));
    
    // Act
    boolean result = userService.deleteUser(1L);
    
    // Assert
    assertTrue(result, "Admin user should be deletable");
    verify(userRepository, times(1)).delete(admin);
}
────────────────────────────────────────────────
Créer ce test ? [y/n/e/a] : a

✅ 2 tests restants créés automatiquement

📊 Résultat :
   - 3 nouveaux tests créés
   - Couverture estimée : 65% → 92%
   - Fichier : src/test/java/.../UserServiceTest.java

Lancer les tests maintenant ? [y/n] : y
```

---

### 4. Mode CI/CD

```bash
# Vérifie le seuil (exit 1 si < seuil)
git-ia-coverage check --fail-under 80

# Utilisé en CI/CD
```

**Exemple GitLab CI** :
```yaml
# .gitlab-ci.yml
test:
  stage: test
  script:
    - mvn test jacoco:report
    - git-ia-coverage check --fail-under 80
  coverage: '/Total coverage: (\d+\.\d+)%/'
```

---

## 🔗 Intégrations

### 1. git-ia-test

```bash
# Génère tests de base + coverage pour compléter
git-ia-test UserService.java
git-ia-coverage generate --file UserService.java --target 90
```

### 2. JIRA

```bash
# Crée ticket JIRA si couverture < seuil
git-ia-coverage jira-ticket --threshold 80 --project MYAPP

# Résultat :
# → Ticket créé : "Améliorer couverture UserService.java (65% → 80%)"
# → Description inclut lignes/branches manquantes
```


```bash
git-ia-coverage sync-sonar --project my-app
```

---

## 📊 Formats de sortie

### Text (console)
```bash
git-ia-coverage analyze

# Affichage tableau avec couleurs
```

### JSON
```bash
git-ia-coverage analyze --format json --output coverage.json

{
  "total_coverage": 75.5,
  "files": [
    {
      "path": "src/UserService.java",
      "coverage": 65.0,
      "lines_total": 120,
      "lines_covered": 78,
      "lines_missing": [45, 46, 47, 78, 92, 93, 94, 95],
      "branches_total": 15,
      "branches_covered": 10
    }
  ],
  "threshold": 80,
  "status": "FAIL"
}
```

### HTML Report
```bash
git-ia-coverage analyze --report html --output coverage-report/

# Génère :
# coverage-report/
# ├── index.html
# ├── src_UserService_java.html
# └── styles.css
```

---

## 🎓 Exemples d'utilisation

### Scénario 1 : Atteindre 80% de couverture

```bash
# 1. Analyser la couverture actuelle
git-ia-coverage analyze --threshold 80

# Sortie :
# ❌ Couverture globale : 68% (seuil : 80%)
# 5 fichiers sous le seuil

# 2. Afficher les fichiers problématiques
git-ia-coverage show --below 80

# 3. Générer tests pour le fichier le plus critique
git-ia-coverage generate --file src/UserService.java --target 85

# 4. Lancer les tests
mvn test

# 5. Vérifier la nouvelle couverture
git-ia-coverage analyze

# ✅ Couverture globale : 82%
```

---

### Scénario 2 : CI/CD bloque si couverture < 80%

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run tests with coverage
        run: |
          pytest --cov=src --cov-report=xml
      
      - name: Check coverage threshold
        run: |
          pip install git-ia-assistant
          git-ia-coverage check --fail-under 80
```

---

## 🚀 Roadmap

### Phase 1 - MVP (1 semaine)
- Support Python (pytest-cov)
- Analyse coverage.xml
- Affichage console

### Phase 2 - Génération tests (2 semaines)
- IA génère tests manquants
- Mode interactif
- Support Java (JaCoCo)

### Phase 3 - Intégrations (1 semaine)
- Intégration JIRA
- Support TypeScript (Istanbul)

---

**Valeur ajoutée** :
- 🎯 Cibles précises : sait exactement quoi tester
- ⏱️ Gain : 1-2h par module
- ✅ Qualité : atteint critères requis automatiquement

**Date de dernière mise à jour** : Mars 2026
