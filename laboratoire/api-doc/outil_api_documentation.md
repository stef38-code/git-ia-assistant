# 📚 Documentation API Auto-Sync

> **Commande** : `git-ia-api-doc`  
> **Statut** : 📝 En développement  
> **Priorité** : 🔵 Moyenne  
> **Effort estimé** : 60 heures

---

## 📋 Vue d'ensemble

### Problème résolu

Les développeurs doivent :
- Maintenir manuellement la documentation API (souvent obsolète)
- Générer spec OpenAPI/Swagger manuellement
- Créer client SDK TypeScript pour consommer l'API backend
- Synchroniser documentation avec les tickets JIRA

**Impact** : 4-6 heures par sprint pour documenter les APIs.

### Solution proposée

`git-ia-api-doc` génère automatiquement :
1. **Spec OpenAPI 3.0** depuis le code source
2. **Client SDK TypeScript** depuis la spec
3. **Documentation Markdown** enrichie par IA
4. **Synchronisation JIRA** (stories par endpoint)

---

## 🎯 Fonctionnalités principales

### 1. Génération de spec OpenAPI

```bash
# Génère spec OpenAPI depuis code source
git-ia-api-doc generate --source src/controllers --format openapi-3.0 --output docs/api.yaml

# Auto-détection du framework
git-ia-api-doc generate --auto-detect spring-boot

# Avec enrichissement IA
git-ia-api-doc enrich --spec docs/api.yaml --add-examples --add-descriptions
```

**Frameworks supportés** :
- **Spring Boot** : scan annotations `@RestController`, `@GetMapping`, etc.
- **FastAPI** : enrichit le schema auto-généré par FastAPI
- **Express.js** : scan routes et middlewares

**Exemple de génération (Spring Boot)** :
```java
// Avant : Controller Java
@RestController
@RequestMapping("/api/users")
public class UserController {
    
    @GetMapping
    public List<User> getAllUsers() {
        return userService.findAll();
    }
    
    @PostMapping
    public User createUser(@RequestBody UserDTO dto) {
        return userService.create(dto);
    }
}

// Après : OpenAPI généré
paths:
  /api/users:
    get:
      summary: Get all users
      description: Retrieve a list of all registered users
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/User'
    post:
      summary: Create a new user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserDTO'
      responses:
        '201':
          description: User created successfully
```

---

### 2. Enrichissement par IA

```bash
# Enrichit une spec OpenAPI existante
git-ia-api-doc enrich --spec docs/api.yaml --add-examples --add-descriptions

# Options :
# --add-examples : génère exemples de requêtes/réponses
# --add-descriptions : descriptions détaillées par IA
# --add-errors : documente codes d'erreur possibles
```

**Avant enrichissement** :
```yaml
paths:
  /api/users/{id}:
    get:
      summary: Get user by ID
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
```

**Après enrichissement IA** :
```yaml
paths:
  /api/users/{id}:
    get:
      summary: Get user by ID
      description: |
        Retrieve detailed information about a specific user by their unique identifier.
        This endpoint requires authentication and returns comprehensive user data
        including profile information, roles, and last login timestamp.
      parameters:
        - name: id
          in: path
          required: true
          description: Unique identifier of the user to retrieve
          schema:
            type: integer
            minimum: 1
          example: 42
      responses:
        '200':
          description: User found and returned successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
              examples:
                basic_user:
                  summary: Regular user
                  value:
                    id: 42
                    name: "John Doe"
                    email: "john@example.com"
                    role: "USER"
                admin_user:
                  summary: Admin user
                  value:
                    id: 1
                    name: "Admin"
                    email: "admin@example.com"
                    role: "ADMIN"
        '404':
          description: User not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
              example:
                code: "USER_NOT_FOUND"
                message: "No user found with ID 42"
        '401':
          description: Unauthorized - valid authentication required
```

---

### 3. Génération de documentation Markdown

```bash
# Génère doc Markdown depuis spec OpenAPI
git-ia-api-doc markdown --spec docs/api.yaml --output docs/API.md

# Avec template personnalisé
git-ia-api-doc markdown --spec docs/api.yaml --template .templates/api-doc.md --output docs/API.md
```

**Exemple de doc générée** :
```markdown
# API Documentation

## Base URL
```
https://api.example.com/v1
```

## Authentication
All endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <your_token>
```

## Endpoints

### Users

#### GET /api/users
Retrieve a list of all users.

**Query Parameters:**
- `page` (integer, optional): Page number (default: 1)
- `size` (integer, optional): Page size (default: 20)

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com"
  }
]
```

#### POST /api/users
Create a new user.

**Request Body:**
```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "password": "securePassword123"
}
```

**Response (201 Created):**
```json
{
  "id": 2,
  "name": "Jane Doe",
  "email": "jane@example.com"
}
```
```

---

### 4. Génération de client SDK

```bash
# Génère client TypeScript depuis spec OpenAPI
git-ia-api-doc generate-client --spec docs/api.yaml --lang typescript --output src/sdk/

# Autres langages supportés :
# --lang typescript (Angular, React)
# --lang java (Spring RestTemplate)
# --lang python (requests, httpx)
```

**Exemple de client généré (TypeScript)** :
```typescript
// src/sdk/api/user.service.ts
import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { User, UserDTO } from '../models';

@Injectable({ providedIn: 'root' })
export class UserService {
  private readonly baseUrl = 'https://api.example.com/v1';

  constructor(private http: HttpClient) {}

  /**
   * Get all users
   * @param page Page number (default: 1)
   * @param size Page size (default: 20)
   * @returns Observable<User[]>
   */
  getAllUsers(page = 1, size = 20): Observable<User[]> {
    return this.http.get<User[]>(`${this.baseUrl}/api/users`, {
      params: { page, size }
    });
  }

  /**
   * Get user by ID
   * @param id User unique identifier
   * @returns Observable<User>
   */
  getUserById(id: number): Observable<User> {
    return this.http.get<User>(`${this.baseUrl}/api/users/${id}`);
  }

  /**
   * Create a new user
   * @param dto User data transfer object
   * @returns Observable<User>
   */
  createUser(dto: UserDTO): Observable<User> {
    return this.http.post<User>(`${this.baseUrl}/api/users`, dto);
  }
}
```

---

### 5. Synchronisation JIRA

```bash
# Crée stories JIRA pour chaque endpoint
git-ia-api-doc sync-jira --spec docs/api.yaml --project MYAPP --auto-create-stories

# Options :
# --label api,backend : ajoute labels aux tickets
# --epic EPIC-123 : associe à un epic
# --dry-run : prévisualise sans créer
```

**Tickets JIRA créés** :
```
Story 1: MYAPP-456
  Title: Implémenter GET /api/users
  Description:
    Endpoint: GET /api/users
    Fonction: Récupérer la liste de tous les utilisateurs
    
    Paramètres query:
    - page (integer, optional): numéro de page
    - size (integer, optional): taille de page
    
    Réponse 200:
    - Array of User objects
    
    Critères d'acceptation:
    - [ ] Endpoint accessible
    - [ ] Pagination fonctionnelle
    - [ ] Tests unitaires > 80%
    - [ ] Documentation OpenAPI à jour
  
  Labels: api, backend, user-management
  Epic: EPIC-123

Story 2: MYAPP-457
  Title: Implémenter POST /api/users
  ...
```

---

## 🔗 Intégrations

### 1. git-ia-doc
```bash
# Enrichit la documentation générée
git-ia-api-doc generate --spec docs/api.yaml
git-ia-doc docs/API.md --enhance
```

### 2. git-ia-commit-version
```bash
# Versionne l'API lors de changements breaking
git-ia-commit-version --api-version 2.0.0
```

### 3. git-ia-changelog
```bash
# Documente les changements d'API dans CHANGELOG.md
git-ia-changelog --api-changes --spec-diff docs/api-v1.yaml docs/api-v2.yaml
```

---

## 📊 Validation de spec

```bash
# Valide la spec OpenAPI
git-ia-api-doc validate --spec docs/api.yaml --strict

# Vérifie la conformité
git-ia-api-doc validate --spec docs/api.yaml --check-examples --check-schemas
```

**Exemple de sortie** :
```
🔍 Validation de docs/api.yaml

✅ Spec OpenAPI valide (version 3.0.3)

Warnings (2) :
⚠️  Path /api/users/{id} : manque exemple pour réponse 404
⚠️  Schema User : property 'email' manque format validation

Suggestions IA :
💡 Ajouter format email pour User.email :
   email:
     type: string
     format: email

💡 Ajouter exemple pour réponse 404 :
   responses:
     '404':
       examples:
         user_not_found:
           value: { "code": "USER_NOT_FOUND", "message": "..." }

Appliquer ces suggestions ? [y/n] : y
✅ Spec mise à jour
```

---

## 🎓 Exemples d'utilisation

### Scénario 1 : Backend Java → Frontend Angular

```bash
# 1. Développeur backend crée controllers Spring Boot
vim src/main/java/com/example/UserController.java

# 2. Génère spec OpenAPI
git-ia-api-doc generate --auto-detect spring-boot --output docs/api.yaml

# 3. Enrichit avec IA
git-ia-api-doc enrich --spec docs/api.yaml --add-examples

# 4. Génère client TypeScript pour Angular
git-ia-api-doc generate-client --spec docs/api.yaml --lang typescript --output frontend/src/sdk/

# 5. Développeur frontend utilise le SDK
# frontend/src/app/users/user-list.component.ts
import { UserService } from '@sdk/api/user.service';

constructor(private userService: UserService) {}

ngOnInit() {
  this.userService.getAllUsers().subscribe(users => {
    this.users = users;
  });
}

# 6. Commit avec doc à jour
git add docs/api.yaml frontend/src/sdk/
git-ia-commit
```

---

### Scénario 2 : Création automatique de stories JIRA

```bash
# 1. Nouvelle spec API créée
vim docs/api-v2.yaml

# 2. Validation
git-ia-api-doc validate --spec docs/api-v2.yaml

# 3. Synchronisation JIRA (dry-run first)
git-ia-api-doc sync-jira --spec docs/api-v2.yaml --project MYAPP --dry-run

# Sortie :
# Stories qui seront créées (5) :
# - MYAPP-123 : Implémenter GET /api/v2/users
# - MYAPP-124 : Implémenter POST /api/v2/users
# ...

# 4. Création effective
git-ia-api-doc sync-jira --spec docs/api-v2.yaml --project MYAPP --epic EPIC-200

# ✅ 5 stories créées et associées à EPIC-200
```

---

## 🚀 Roadmap

### Phase 1 - MVP (3 semaines)
- Génération OpenAPI (Spring Boot)
- Enrichissement IA basique
- Documentation Markdown

### Phase 2 - Multi-framework (2 semaines)
- Support FastAPI
- Support Express.js
- Validation de spec

### Phase 3 - Client SDK (2 semaines)
- Génération TypeScript
- Génération Java
- Génération Python

### Phase 4 - Intégrations (1 semaine)
- Synchronisation JIRA
- git-ia-changelog
- Export Confluence

---

**Valeur ajoutée** :
- 📚 Documentation toujours à jour
- ⏱️ Gain : 4-6h par sprint
- 🔗 Synchronisation backend ↔ frontend automatique

**Date de dernière mise à jour** : Mars 2026
