# Cours FastAPI — Backend HoopsData Step 1

*Cours interactif, orienté projet. Objectif : à la fin, tu as un backend fonctionnel qui gère les matchs, leurs métadonnées et leurs statuts, prêt à recevoir le stockage vidéo et le frontend.*

---

## Comment on travaille

- **Chaque module** = concept expliqué → QCM → exercice sur le vrai projet.
- **Les snippets du cours ne sont pas la solution.** Ils montrent la syntaxe sur des exemples génériques (`items`, `users`). À toi de transposer sur `matches`.
- **Tu codes, tu m'envoies, je corrige.** Pas de corrigé pour les exercices dans ce document. Les réponses des QCM sont en annexe.
- **Critères de validation** à la fin de chaque exercice : tant qu'ils ne passent pas, on ne passe pas au module suivant.
- Environnement : Windows, Python 3.11+, VS Code, terminal PowerShell.

Le projet que tu construis module après module s'appelle `hoopsdata-api`. Un seul dossier, qui grossit.

---

## Module 0 — Installer et lancer un premier serveur

### Concepts

**Un serveur web**, c'est un programme qui tourne en boucle, écoute sur un **port** (un numéro, ex. 8000), et répond à des requêtes HTTP. Ton navigateur envoie `GET http://localhost:8000/health`, le serveur exécute la fonction associée et renvoie une réponse.

**FastAPI** est la bibliothèque qui te permet de déclarer "quand on appelle cette URL, exécute cette fonction Python". **Uvicorn** est le serveur qui fait tourner ton app FastAPI. Les deux vont ensemble.

**Le venv** isole les dépendances du projet. Tu en as déjà un pour le pipeline ; celui-ci est séparé.

```powershell
mkdir hoopsdata-api
cd hoopsdata-api
python -m venv .venv
.venv\Scripts\activate
pip install "fastapi[standard]" sqlalchemy pydantic-settings pytest httpx
```

Un fichier `main.py` minimal :

```python
from fastapi import FastAPI

app = FastAPI(title="Mon API")


@app.get("/")
def root():
    return {"message": "hello"}
```

Le décorateur `@app.get("/")` dit : "la requête GET sur `/` déclenche `root()`". Le dict retourné est converti automatiquement en JSON.

Lancer :

```powershell
fastapi dev main.py
```

Puis ouvrir `http://localhost:8000/docs`. C'est **Swagger UI**, généré automatiquement à partir de ton code. Chaque route y apparaît avec un bouton "Try it out". C'est ton outil de test principal pendant tout le cours — tu n'as pas besoin de frontend pour vérifier que ton backend marche.

`fastapi dev` recharge automatiquement le serveur à chaque sauvegarde de fichier.

### QCM 0

**Q0.1** — Que fait Uvicorn ?
- a) Il valide les données
- b) Il fait tourner l'app FastAPI et écoute sur un port
- c) Il génère la page `/docs`
- d) Il gère la base de données

**Q0.2** — Tu retournes un `dict` Python depuis une route. Que reçoit le client ?
- a) Une erreur, il faut retourner une string
- b) Du JSON
- c) Un objet Python sérialisé en pickle
- d) Du HTML

**Q0.3** — Où est générée la doc interactive ?
- a) Tu dois l'écrire à la main dans un fichier YAML
- b) Elle est déduite du code (décorateurs, types, signatures)
- c) Elle vient d'un plugin VS Code
- d) Elle n'existe qu'en production

### Exercice 0

Crée le projet `hoopsdata-api`, installe les dépendances, écris `main.py` avec :

- `GET /health` qui retourne `{"status": "ok", "service": "hoopsdata-api"}`
- Un titre d'app `HoopsData API` et une version `0.1.0` (regarde les paramètres de `FastAPI(...)`)

**Validation :**
- `http://localhost:8000/health` affiche le JSON attendu
- `/docs` montre le titre "HoopsData API" et la route `/health`
- Modifier le texte retourné et sauvegarder recharge le serveur sans le relancer

---

## Module 1 — Routes, paramètres, codes HTTP

### Concepts

**Les verbes HTTP** décrivent l'intention :

| Verbe | Sens | Exemple HoopsData |
|---|---|---|
| GET | Lire, sans effet de bord | Lister les matchs |
| POST | Créer | Déclarer un nouveau match |
| PATCH | Modifier partiellement | Changer le statut |
| DELETE | Supprimer | Supprimer un match |

**Paramètre de chemin** : une partie variable de l'URL. Déclaré entre accolades, récupéré comme argument de fonction, typé.

```python
@app.get("/items/{item_id}")
def get_item(item_id: int):
    return {"item_id": item_id}
```

Si on appelle `/items/abc`, FastAPI renvoie **422** tout seul parce que `abc` n'est pas un `int`. Le typage n'est pas décoratif : il valide.

**Paramètre de requête** : tout ce qui est après `?` dans l'URL. Tout argument de fonction qui n'est pas dans le chemin est automatiquement un query param.

```python
@app.get("/items")
def list_items(category: str | None = None, limit: int = 20): ...
```

→ `/items?category=shoes&limit=5`. Le `= None` le rend optionnel.

**Codes de statut** : la réponse HTTP porte un code numérique.

| Code | Sens |
|---|---|
| 200 | OK |
| 201 | Créé (à utiliser sur POST) |
| 404 | Introuvable |
| 422 | Données invalides (FastAPI le génère automatiquement) |
| 500 | Bug côté serveur |

Pour renvoyer une erreur volontairement :

```python
from fastapi import HTTPException

if item is None:
    raise HTTPException(status_code=404, detail="Item not found")
```

Pour fixer le code d'une route qui réussit :

```python
@app.post("/items", status_code=201)
```

### QCM 1

**Q1.1** — Route `GET /matches/{match_id}` avec `match_id: int`. On appelle `/matches/xyz`. Résultat ?
- a) 404
- b) 422
- c) 500
- d) Ça passe, `match_id` vaut `"xyz"`

**Q1.2** — Quel verbe pour "passer le statut d'un match à `uploaded`" ?
- a) GET
- b) POST
- c) PATCH
- d) PUT

**Q1.3** — `/matches?status=uploaded&level=varsity`. Combien de query params ?
- a) 0, ce sont des path params
- b) 1
- c) 2
- d) Ça dépend de la fonction

**Q1.4** — Pourquoi 201 plutôt que 200 sur un POST qui crée une ressource ?
- a) C'est plus rapide
- b) Ça indique explicitement au client qu'une ressource a été créée
- c) 200 est interdit sur POST
- d) Aucune différence, convention arbitraire

### Exercice 1

Toujours dans `main.py`, sans base de données. Crée une liste Python en dur avec 3 matchs (des dicts avec `id`, `home_team`, `away_team`, `status`). Puis :

- `GET /matches` : renvoie la liste. Accepte un query param optionnel `status` qui filtre.
- `GET /matches/{match_id}` : renvoie le match, ou 404 avec un message clair.

**Validation :**
- `/matches` renvoie les 3
- `/matches?status=uploaded` ne renvoie que ceux qui ont ce statut
- `/matches/999` renvoie 404 avec `{"detail": "..."}`
- `/matches/abc` renvoie 422 (sans que tu aies rien codé pour ça)

---

## Module 2 — Pydantic : valider ce qui entre et ce qui sort

### Concepts

Un `POST` envoie un **corps de requête** (body) en JSON. Tu ne veux pas le recevoir comme un dict brut et vérifier chaque champ à la main. **Pydantic** définit un **schéma** : les champs, leurs types, leurs contraintes. FastAPI valide le body contre ce schéma avant même d'entrer dans ta fonction.

```python
from pydantic import BaseModel, Field
from datetime import date
from enum import Enum


class Category(str, Enum):
    shoes = "shoes"
    shirts = "shirts"


class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    category: Category
    release_date: date
    note: str | None = None
```

- `str, Enum` : une liste fermée de valeurs. Envoyer `"hats"` → 422 automatique.
- `date` : Pydantic parse `"2026-09-03"` en objet `date`.
- `Field(...)` : contraintes supplémentaires.
- `str | None = None` : optionnel.

Dans la route :

```python
@app.post("/items", status_code=201)
def create_item(item: ItemCreate):
    return item
```

Un argument typé avec un `BaseModel` = c'est le body. FastAPI le sait tout seul.

**Deux schémas, pas un.** Ce que le client *envoie* et ce que le serveur *renvoie* ne sont pas la même chose. Le client n'envoie pas l'`id`, ni la date de création, ni le statut initial : c'est le serveur qui les génère. D'où le pattern :

- `XxxCreate` : ce que le client fournit
- `XxxOut` : ce que le serveur renvoie (= Create + les champs générés)

```python
class ItemOut(ItemCreate):
    id: str
    created_at: datetime
```

Et sur la route, `response_model=ItemOut` : FastAPI filtre et valide la réponse, et la doc affiche le bon schéma.

**Générer un identifiant unique.** Deux options :

- `uuid.uuid4()` → `"3f2a9c1e-..."`. Unique, sans coordination, illisible.
- Un ID lisible du type `M-20260903-7K2Q` (préfixe + date + suffixe aléatoire). Plus agréable pour ton équipe qui va le voir dans une liste. Attention au risque de collision si le suffixe est trop court.

Pour ce cours, on part sur UUID (fiable), tu pourras ajouter un ID lisible en champ secondaire plus tard.

### QCM 2

**Q2.1** — Champ `level: Level` où `Level` est un `str, Enum` avec `varsity`, `jv`, `freshman`. Le client envoie `"Varsity"` (majuscule). Résultat ?
- a) Accepté et normalisé
- b) 422
- c) Accepté tel quel
- d) 500

**Q2.2** — Pourquoi séparer `MatchCreate` et `MatchOut` ?
- a) Performance
- b) Le client ne doit pas fournir les champs générés par le serveur (id, statut, created_at)
- c) Pydantic l'impose
- d) Pour avoir deux pages dans `/docs`

**Q2.3** — Dans une route, un argument typé `MatchCreate` est interprété comme :
- a) Un query param
- b) Un path param
- c) Le body JSON
- d) Un header

**Q2.4** — `uuid4()` garantit l'unicité comment ?
- a) En consultant la base
- b) En incrémentant un compteur global
- c) Par aléatoire sur 122 bits, collision statistiquement négligeable
- d) Il ne la garantit pas

### Exercice 2

Crée un fichier `schemas.py` avec :

- `Level(str, Enum)` : `varsity`, `jv`, `freshman`
- `MatchStatus(str, Enum)` : `pending_upload`, `uploaded`, `processing`, `done`, `failed`
- `MatchCreate` : `home_team`, `away_team`, `game_date` (date), `level`, `uploaded_by`. Contraintes : noms d'équipe entre 1 et 80 caractères ; `home_team != away_team` (cherche `model_validator` dans la doc Pydantic v2).
- `MatchOut` : hérite de `MatchCreate` + `id: str`, `status: MatchStatus`, `created_at: datetime`, `video_key: str | None`

Dans `main.py`, remplace la liste en dur par une liste vide, puis :

- `POST /matches` : reçoit un `MatchCreate`, génère un UUID, statut `pending_upload`, `created_at` = maintenant (UTC), ajoute à la liste, renvoie 201 avec `response_model=MatchOut`
- Adapte `GET /matches` et `GET /matches/{match_id}` avec `response_model`

**Validation :**
- Depuis `/docs`, créer un match valide renvoie 201 et un objet avec `id`, `status`, `created_at`
- Envoyer `level: "pro"` renvoie 422
- Envoyer la même équipe en home et away renvoie 422
- Envoyer `game_date: "hier"` renvoie 422
- `/docs` affiche les enums comme des listes déroulantes

---

## Module 3 — SQLAlchemy et SQLite : persister

### Concepts

Ta liste Python disparaît à chaque redémarrage. Il faut une base.

**SQLAlchemy** est un ORM : tu déclares des classes Python, il crée les tables et traduit tes opérations en SQL. Tu n'écris pas de SQL à la main pour le CRUD basique.

Quatre pièces :

**1. L'engine** : la connexion à la base. Pour SQLite, c'est un chemin de fichier.

```python
from sqlalchemy import create_engine

engine = create_engine("sqlite:///./app.db", connect_args={"check_same_thread": False})
```

(`check_same_thread` est une spécificité SQLite + FastAPI, pas besoin avec Postgres.)

**2. La session** : une "conversation" avec la base. On en ouvre une par requête HTTP, on la ferme à la fin.

```python
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(bind=engine)
```

**3. Le modèle** : une classe = une table, un attribut = une colonne.

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = "items"
    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    note: Mapped[str | None]
```

`Base.metadata.create_all(engine)` crée les tables si elles n'existent pas.

**4. La dépendance** : comment chaque route obtient sa session. C'est le mécanisme `Depends` de FastAPI.

```python
from fastapi import Depends
from sqlalchemy.orm import Session


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/items")
def list_items(db: Session = Depends(get_db)):
    return db.query(Item).all()
```

`Depends(get_db)` : avant d'exécuter la route, FastAPI appelle `get_db()`, injecte le résultat, et après la route, exécute le `finally`. Une session propre par requête, fermée quoi qu'il arrive.

**Opérations de base :**

```python
db.add(obj)  # préparer l'insertion
db.commit()  # écrire
db.refresh(obj)  # recharger depuis la base (utile après commit)
db.query(Item).filter(Item.id == some_id).first()
db.query(Item).order_by(Item.created_at.desc()).all()
db.delete(obj)
db.commit()
```

**Le pont ORM → Pydantic.** Pour que `response_model=ItemOut` accepte un objet SQLAlchemy (et pas un dict), ajoute dans le schéma Pydantic :

```python
class ItemOut(BaseModel):
    model_config = {"from_attributes": True}
    ...
```

**Enums en base.** Un `str, Enum` Pydantic se stocke comme une colonne texte. Côté SQLAlchemy : `Mapped[str]` suffit, ou `mapped_column(SAEnum(MatchStatus))` si tu veux que la base refuse les valeurs hors liste. Commence simple : texte.

**Modèle vs schéma** — tu vas avoir deux classes `Match` : le modèle SQLAlchemy (`models.py`, la table) et le schéma Pydantic (`schemas.py`, le contrat JSON). Elles se ressemblent, elles n'ont pas le même rôle. Ne les fusionne pas.

### QCM 3

**Q3.1** — À quoi sert `yield` dans `get_db()` ?
- a) À rendre la fonction asynchrone
- b) À fournir la session à la route puis reprendre après pour la fermer
- c) À créer un générateur de sessions multiples
- d) C'est une convention sans effet

**Q3.2** — Tu fais `db.add(match)` sans `db.commit()`. Résultat ?
- a) Le match est en base
- b) Le match n'est pas en base, l'insertion est annulée à la fermeture de la session
- c) Erreur immédiate
- d) Le match est en base mais sans id

**Q3.3** — `from_attributes = True` sert à :
- a) Autoriser Pydantic à lire des objets par attributs (ex. objets SQLAlchemy) et pas seulement des dicts
- b) Activer la validation
- c) Rendre les champs optionnels
- d) Rien en Pydantic v2

**Q3.4** — Tu redémarres le serveur. Les données SQLite :
- a) Disparaissent
- b) Restent, elles sont dans le fichier `.db`
- c) Restent seulement si tu as appelé `create_all`
- d) Restent mais deviennent en lecture seule

### Exercice 3

Crée `database.py` (engine, SessionLocal, Base, get_db) et `models.py` (modèle `Match` avec toutes les colonnes de `MatchOut`). Dans `main.py`, appelle `create_all` au démarrage et remplace la liste en mémoire par la base dans les trois routes.

**Validation :**
- Un fichier `hoopsdata.db` apparaît dans le dossier après le premier lancement
- Tu crées 2 matchs, tu arrêtes le serveur, tu le relances, `GET /matches` les renvoie toujours
- `GET /matches` les renvoie triés du plus récent au plus ancien
- Ouvre le `.db` avec l'extension VS Code "SQLite Viewer" et regarde ta table

---

## Module 4 — Le CRUD complet et le cycle de vie du statut

### Concepts

**Modification partielle.** Un `PATCH` ne renvoie que les champs qui changent. Schéma dédié, tout optionnel :

```python
class ItemUpdate(BaseModel):
    name: str | None = None
    note: str | None = None
```

Et dans la route, n'appliquer que ce qui a été envoyé :

```python
data = payload.model_dump(exclude_unset=True)
for key, value in data.items():
    setattr(item, key, value)
db.commit()
```

`exclude_unset=True` distingue "le client n'a pas envoyé ce champ" de "le client a envoyé `null`".

**Machine à états.** Le statut d'un match ne peut pas passer de `done` à `pending_upload`. Il faut définir les transitions autorisées :

```python
ALLOWED = {
    "draft": {"active"},
    "active": {"archived"},
}


def can_transition(current, target):
    return target in ALLOWED.get(current, set())
```

Une transition interdite → 409 Conflict (le code standard pour "l'état actuel ne permet pas cette opération").

**Pagination.** Ne jamais renvoyer toute la table sans limite. Query params `limit` (défaut 50, max 200) et `offset`.

```python
db.query(Item).offset(offset).limit(limit).all()
```

Tu peux borner un query param : `limit: int = Query(50, ge=1, le=200)`.

**Suppression.** `DELETE /items/{id}` → 204 No Content, pas de body. Question projet : faut-il vraiment supprimer un match ou le marquer supprimé ? Pour le Step 1, suppression réelle, c'est une plateforme interne.

### QCM 4

**Q4.1** — `PATCH /matches/{id}` avec un body vide `{}`. Comportement correct ?
- a) 422
- b) 200, rien ne change
- c) 404
- d) Tous les champs sont mis à `null`

**Q4.2** — Le match est `done`, le client demande `status: "uploaded"`. Code ?
- a) 200
- b) 400
- c) 409
- d) 422

**Q4.3** — `limit: int = Query(50, ge=1, le=200)`. Client envoie `limit=500`. Résultat ?
- a) Tronqué à 200
- b) 422
- c) 50
- d) 500 résultats

**Q4.4** — Différence entre `exclude_unset` et `exclude_none` ?
- a) Aucune
- b) `unset` = pas envoyé ; `none` = envoyé avec valeur `null`
- c) `unset` est pour les enums
- d) `none` est déprécié

### Exercice 4

Dans `schemas.py`, ajoute `MatchUpdate` (statut, `video_key`, tous optionnels — les métadonnées ne sont pas modifiables via PATCH pour l'instant, décision assumée).

Dans `main.py` :

- `PATCH /matches/{match_id}` avec machine à états. Transitions autorisées : `pending_upload → uploaded`, `uploaded → processing`, `processing → done`, `processing → failed`, `failed → processing`. Transition interdite → 409.
- `DELETE /matches/{match_id}` → 204
- Pagination sur `GET /matches` avec `limit` (1–200, défaut 50) et `offset`
- Filtres sur `GET /matches` : `status`, `level`, `uploaded_by`, tous optionnels et cumulables

**Validation :**
- `pending_upload → uploaded` marche, `uploaded → done` renvoie 409 avec un message qui indique la transition refusée
- `DELETE` puis `GET` sur le même id → 404
- `/matches?level=varsity&status=uploaded&limit=2` filtre et limite correctement
- `limit=0` → 422

---

## Module 5 — Structurer le projet, configurer, ouvrir au frontend

### Concepts

`main.py` devient trop gros. Structure cible :

```
hoopsdata-api/
  app/
    __init__.py
    main.py          # crée l'app, monte les routers, middleware
    config.py        # settings
    database.py
    models.py
    schemas.py
    routers/
      __init__.py
      matches.py     # toutes les routes /matches
  tests/
  .env
  .gitignore
  requirements.txt
```

**Les routers** découpent les routes par domaine :

```python
# app/routers/items.py
from fastapi import APIRouter
router = APIRouter(prefix="/items", tags=["items"])

@router.get("")
def list_items(...): ...

# app/main.py
from app.routers import items
app.include_router(items.router)
```

`tags` regroupe les routes dans `/docs`.

**La configuration.** Jamais de chemin de base ou de clé API en dur dans le code. Tout passe par des variables d'environnement, lues par `pydantic-settings` :

```python
# app/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./app.db"
    app_env: str = "dev"
    model_config = {"env_file": ".env"}


settings = Settings()
```

Un fichier `.env` (jamais commité, dans `.gitignore`) :

```
DATABASE_URL=sqlite:///./hoopsdata.db
APP_ENV=dev
```

C'est exactement ici que se fera la bascule SQLite → Postgres : une ligne dans `.env`, zéro changement de code.

**CORS.** Ton futur frontend React tournera sur `localhost:5173`, ton API sur `localhost:8000`. Pour le navigateur, ce sont deux origines différentes, et par défaut il **bloque** les appels de l'une vers l'autre. Le serveur doit explicitement autoriser :

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Sans ça, le frontend recevra des erreurs CORS incompréhensibles. La liste des origines autorisées a sa place dans `Settings`.

**Lancement** avec la nouvelle structure : `fastapi dev app/main.py`.

### QCM 5

**Q5.1** — Pourquoi `.env` est dans `.gitignore` ?
- a) Il est trop gros
- b) Il contiendra des secrets (clés R2, URL Postgres avec mot de passe)
- c) Git ne supporte pas ce format
- d) Par convention sans raison

**Q5.2** — CORS est appliqué par :
- a) FastAPI côté serveur pour bloquer
- b) Le navigateur, qui refuse d'exploiter la réponse si le serveur n'a pas autorisé l'origine
- c) Uvicorn
- d) Le système d'exploitation

**Q5.3** — `APIRouter(prefix="/matches")` puis `@router.get("/{match_id}")`. URL finale ?
- a) `/{match_id}`
- b) `/matches/{match_id}`
- c) `/matches//{match_id}`
- d) Erreur

**Q5.4** — Un script Python qui appelle ton API avec `requests` est-il concerné par CORS ?
- a) Oui
- b) Non, CORS n'existe que dans les navigateurs
- c) Seulement en HTTPS
- d) Seulement pour POST

### Exercice 5

Refactorise selon la structure cible. Aucune fonctionnalité nouvelle. Ajoute `config.py` avec `database_url` et `cors_origins` (liste), `.env`, `.gitignore`, `requirements.txt` (`pip freeze > requirements.txt`), et le middleware CORS.

Initialise un dépôt git si ce n'est pas fait.

**Validation :**
- `fastapi dev app/main.py` démarre sans erreur
- Tout l'exercice 4 marche encore, à l'identique
- `/docs` montre un groupe "matches"
- Changer `DATABASE_URL` dans `.env` vers un autre nom de fichier crée une nouvelle base vide
- `git status` ne montre ni `.env`, ni `.venv`, ni `*.db`

---

## Module 6 — Tests automatisés

### Concepts

Tester à la main dans `/docs` ne scale pas. À chaque modification, tu veux relancer 20 vérifications en une commande.

**pytest** découvre les fichiers `test_*.py` et exécute les fonctions `test_*`. **TestClient** simule des requêtes HTTP sans lancer de serveur.

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
```

**Base de test isolée.** Tes tests ne doivent pas écrire dans `hoopsdata.db`. Le mécanisme : **remplacer la dépendance `get_db`** par une version qui pointe vers une base jetable.

```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app


@pytest.fixture
def client(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path}/test.db", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
```

`tmp_path` est un dossier temporaire fourni par pytest, détruit après le test. `dependency_overrides` est la porte que FastAPI laisse ouverte exactement pour ça. Chaque test reçoit une base vide.

Une fixture, c'est une fonction dont le résultat est injecté dans les tests qui la nomment en argument. Même logique que `Depends`, côté pytest.

**Ce qu'on teste** : pas le framework, ton comportement. Les cas nominaux, les erreurs (404, 409, 422), les transitions.

### QCM 6

**Q6.1** — Pourquoi `dependency_overrides` plutôt qu'un `if TESTING:` dans `database.py` ?
- a) C'est plus rapide
- b) Le code de prod ne contient aucune logique de test, on substitue de l'extérieur
- c) `if` n'est pas autorisé dans FastAPI
- d) Aucune différence

**Q6.2** — Deux tests créent chacun un match. Le second en voit combien avec la fixture ci-dessus ?
- a) 2
- b) 1
- c) 0
- d) Dépend de l'ordre

**Q6.3** — `TestClient` lance-t-il un vrai serveur sur un port ?
- a) Oui, sur 8000
- b) Oui, sur un port aléatoire
- c) Non, il appelle l'app directement en mémoire
- d) Seulement si Uvicorn est installé

### Exercice 6

Crée `tests/conftest.py` et `tests/test_matches.py` avec au minimum :

1. Créer un match valide → 201, `status == "pending_upload"`, `id` non vide
2. Créer avec `level` invalide → 422
3. `GET` sur un id inconnu → 404
4. Transition `pending_upload → uploaded` → 200 ; puis `uploaded → done` → 409
5. Créer 3 matchs, `GET /matches?limit=2` en renvoie 2
6. `DELETE` puis `GET` → 404

**Validation :**
- `pytest -v` : tout vert
- `hoopsdata.db` n'a pas bougé après les tests
- Casse volontairement une transition dans ton code → un test rouge te le dit

---

## Module 7 — Le pont vers le Step 1 complet : préparer l'upload

### Concepts

Ton backend gère les métadonnées. Il manque le lien avec la vidéo. Voici ce qui arrive après ce cours, et ce que tu peux déjà préparer.

**Rappel du flux d'upload :**

1. Client → `POST /matches` → reçoit l'id (fait)
2. Client → `POST /matches/{id}/upload-url` → reçoit une URL pré-signée
3. Client → envoie la vidéo directement au stockage via cette URL
4. Client → `POST /matches/{id}/complete` → statut `uploaded`, `video_key` enregistré
5. Client → `GET /matches/{id}/preview-url` → URL pré-signée en lecture pour la balise `<video>`

**Une URL pré-signée**, c'est une URL vers le stockage qui contient une signature cryptographique générée avec ta clé secrète. Elle autorise *une* opération (PUT ou GET), sur *un* objet, pendant *une* durée limitée. Le client peut l'utiliser sans connaître ta clé. C'est le stockage lui-même qui vérifie la signature.

Cloudflare R2 expose la même API que S3, donc la bibliothèque est **boto3** (le SDK AWS) pointée vers R2. Le code, à titre d'aperçu — tu ne l'écris pas maintenant :

```python
import boto3

s3 = boto3.client(
    "s3",
    endpoint_url=settings.r2_endpoint,
    aws_access_key_id=settings.r2_key,
    aws_secret_access_key=settings.r2_secret,
)
url = s3.generate_presigned_url(
    "put_object", Params={"Bucket": "videos", "Key": key}, ExpiresIn=3600
)
```

**Le `video_key`**, c'est le chemin de l'objet dans le bucket. Convention à décider maintenant : `matches/{match_id}/raw.mp4` est simple et évite les collisions puisque l'id est unique.

**Pourquoi mocker.** Tu peux écrire ces trois routes dès maintenant avec un service de stockage **factice** qui renvoie de fausses URLs. Le contrat d'API sera fixé, le frontend pourra être développé contre, et brancher R2 reviendra à remplacer une classe. C'est le même principe que `dependency_overrides` : une interface, deux implémentations.

```python
class FakeStorage:
    def presigned_put(self, key: str) -> str:
        return f"https://fake-storage.local/put/{key}"

    def presigned_get(self, key: str) -> str:
        return f"https://fake-storage.local/get/{key}"
```

Injectée via `Depends`, comme la base.

### QCM 7

**Q7.1** — La clé secrète R2 transite-t-elle vers le navigateur ?
- a) Oui, dans l'URL
- b) Non, seule la signature calculée avec cette clé y figure
- c) Oui, dans un header
- d) Seulement pour le GET

**Q7.2** — Une URL pré-signée PUT valable 1h. Après 1h ?
- a) Elle marche encore si l'upload a commencé avant
- b) Le stockage refuse
- c) Elle devient GET
- d) Le backend doit la révoquer

**Q7.3** — Pourquoi la vidéo ne passe-t-elle pas par FastAPI ?
- a) FastAPI ne sait pas lire les fichiers
- b) Pour ne pas saturer la bande passante et la mémoire d'un petit serveur avec des Go de données qui ne font que transiter
- c) Question de sécurité uniquement
- d) Parce que R2 l'interdit

**Q7.4** — `POST /matches/{id}/complete` sur un match `done`. Code ?
- a) 200
- b) 409
- c) 404
- d) 422

### Exercice final

Ajoute au projet, avec un `FakeStorage` injecté par `Depends` :

- `POST /matches/{id}/upload-url` → `{"upload_url": ..., "video_key": ...}`. 404 si inconnu, 409 si le statut n'est pas `pending_upload`.
- `POST /matches/{id}/complete` → passe en `uploaded`, enregistre `video_key`, renvoie le `MatchOut`. 409 si pas `pending_upload`.
- `GET /matches/{id}/preview-url` → `{"preview_url": ...}`. 409 si pas de `video_key`.
- Tests pour les trois, y compris les 409.
- Un `README.md` : comment installer, lancer, tester. Trois paragraphes suffisent.

**Validation :**
- Le scénario complet (créer → upload-url → complete → preview-url) passe dans `/docs` et dans un test
- `pytest` tout vert
- Quelqu'un qui clone le dépôt et lit le README peut lancer l'API en cinq minutes

Quand ce jalon passe, le backend du Step 1 est prêt. Il ne reste que : remplacer `FakeStorage` par R2, le frontend, le déploiement.

---

## Annexe A — Réponses des QCM

**Module 0** — 0.1 b · 0.2 b · 0.3 b

**Module 1** — 1.1 b (validation de type = 422, avant même d'atteindre ta fonction) · 1.2 c · 1.3 c · 1.4 b

**Module 2** — 2.1 b (les enums sont sensibles à la casse ; si tu veux tolérer, normalise dans un validateur) · 2.2 b · 2.3 c · 2.4 c

**Module 3** — 3.1 b · 3.2 b · 3.3 a · 3.4 b (`create_all` crée les tables, ne touche pas aux données)

**Module 4** — 4.1 b (un PATCH vide est valide : rien à changer) · 4.2 c · 4.3 b · 4.4 b

**Module 5** — 5.1 b · 5.2 b · 5.3 b · 5.4 b

**Module 6** — 6.1 b · 6.2 c (base jetable par test) · 6.3 c

**Module 7** — 7.1 b · 7.2 b · 7.3 b · 7.4 b

---

## Annexe B — Erreurs fréquentes

| Symptôme | Cause probable |
|---|---|
| `ModuleNotFoundError: app` | Tu lances depuis le mauvais dossier ; place-toi à la racine de `hoopsdata-api` |
| `Address already in use` | Un ancien serveur tourne encore ; ferme-le ou change de port (`--port 8001`) |
| 422 alors que le body semble correct | Regarde `detail` dans la réponse : il dit exactement quel champ et pourquoi |
| `response_model` renvoie 500 "validation error" | Ton objet SQLAlchemy ne matche pas le schéma, ou `from_attributes` manque |
| `sqlite3.OperationalError: database is locked` | Deux processus écrivent ; ferme le SQLite Viewer ou le serveur en double |
| Données perdues après modification d'un modèle | `create_all` ne modifie pas une table existante ; supprime le `.db` en dev (plus tard : Alembic) |
| CORS error dans la console du navigateur | Origine du frontend absente de `allow_origins` |
| Les tests écrivent dans la vraie base | `dependency_overrides` mal positionné ou fixture non utilisée |

---

## Annexe C — Commandes

```powershell
.venv\Scripts\activate
fastapi dev app/main.py
pytest -v
pytest -v -k "transition"      # un sous-ensemble
pip freeze > requirements.txt
```

---

*Fin du cours. Envoie-moi ton code module par module.*
