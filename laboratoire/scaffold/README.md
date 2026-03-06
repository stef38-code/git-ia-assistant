# 🏗️ Génération de Composants Full-Stack

> **Commande** : `git-ia-scaffold`  
> **Statut** : 📝 En développement  
> **Priorité** : 🟠 Haute  
> **Effort estimé** : 80 heures

---

## 📋 Vue d'ensemble

`git-ia-scaffold` génère automatiquement du code structurel complet (composants, services, entités) avec :
- Code source conforme aux patterns du projet
- Tests unitaires et d'intégration
- Documentation générée automatiquement

---

## 🎯 Sous-scénarios

Ce scénario est divisé en 3 fichiers détaillés :

### 1. [Spring Boot - Controller/Service/Entity](./spring_boot_scaffold.md)
Génération de code backend Java/Spring Boot :
- Entités JPA avec relations
- Repositories, Services, Controllers REST
- Tests JUnit 5 + MockMvc

### 2. [Angular - Component/Service/Model](./angular_scaffold.md)
Génération de code frontend Angular :
- Composants avec routing, forms, pipes
- Services HttpClient
- Models TypeScript
- Tests Jasmine/Karma

### 3. [FastAPI - Route/Schema/Model](./fastapi_scaffold.md)
Génération de code backend Python/FastAPI :
- Routes REST avec Pydantic
- Models SQLAlchemy
- Tests pytest
- Migrations Alembic

---

## 🚀 Utilisation rapide

```bash
# Spring Boot
git-ia-scaffold entity --name User --fields "id:Long,name:String,email:String" --jpa

# Angular
git-ia-scaffold component --name UserList --features routing,reactive-forms

# FastAPI
git-ia-scaffold route --name users --methods GET,POST,PUT,DELETE --orm sqlalchemy
```

---

## 🔗 Intégrations

- **git-ia-test** : génère tests supplémentaires
- **git-ia-doc** : documente les composants générés
- **git-ia-commit** : commit automatique

---

**Valeur ajoutée** :
- ⏱️ Gain : 30-60 min par composant
- 🎯 Cohérence : patterns projet respectés
- 🧪 Tests inclus : couverture immédiate

**Date de dernière mise à jour** : Mars 2026
