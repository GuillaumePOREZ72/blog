# ![Node.js](https://img.shields.io/badge/Node.js-339933?style=flat&logo=node.js&logoColor=white) ![React](https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=black) ![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) ![Flask](https://img.shields.io/badge/Flask-000000?style=flat&logo=flask&logoColor=white)

# Blog

## Description du projet

Ce projet est une application de blog qui permet aux utilisateurs de créer, lire et gérer des articles de blog. Il est construit avec une architecture en deux parties : un backend en Python utilisant Flask et un frontend en React. L'application vise à fournir une interface utilisateur intuitive pour interagir avec le contenu du blog.

### Fonctionnalités clés
- Création et gestion d'articles de blog
- Affichage des articles dans une liste
- Détails des articles individuels
- Interface utilisateur réactive

## Stack Technologique

| Technologie        | Description                          |
|--------------------|--------------------------------------|
| ![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) | Langage de programmation utilisé pour le backend |
| ![Flask](https://img.shields.io/badge/Flask-000000?style=flat&logo=flask&logoColor=white)   | Framework web pour le développement backend |
| ![Node.js](https://img.shields.io/badge/Node.js-339933?style=flat&logo=node.js&logoColor=white) | Environnement d'exécution JavaScript pour le frontend |
| ![React](https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=black)   | Bibliothèque JavaScript pour la construction d'interfaces utilisateur |
| ![Tailwind CSS](https://img.shields.io/badge/Tailwind%20CSS-06B6D4?style=flat&logo=tailwind-css&logoColor=white) | Framework CSS pour le style des composants |

## Instructions d'installation

### Prérequis
- Python 3.11 ou supérieur
- Node.js et npm (ou pnpm) installés
- Un environnement virtuel Python (recommandé)

### Étapes d'installation

1. **Clonez le dépôt :**
   ```bash
   git clone https://github.com/GuillaumePOREZ72/blog.git
   cd blog
   ```

2. **Installation du backend :**
   - Accédez au répertoire backend :
     ```bash
     cd backend
     ```
   - Créez un environnement virtuel (facultatif mais recommandé) :
     ```bash
     python -m venv venv
     source venv/bin/activate  # Sur Windows utilisez venv\Scripts\activate
     ```
   - Installez les dépendances :
     ```bash
     pip install -r requirements.txt  # Assurez-vous d'avoir un fichier requirements.txt
     ```

3. **Installation du frontend :**
   - Accédez au répertoire frontend :
     ```bash
     cd ../frontend
     ```
   - Installez les dépendances :
     ```bash
     npm install  # ou pnpm install
     ```

4. **Configuration de l'environnement :**
   - Créez un fichier `.env` à la racine du répertoire `backend` et définissez les variables d'environnement nécessaires (exemple) :
     ```
     DATABASE_URL=your_database_url
     SECRET_KEY=your_secret_key
     ```

## Utilisation

### Lancer le backend
- Accédez au répertoire backend et exécutez :
  ```bash
  python app/main.py
  ```
- Le serveur backend devrait démarrer sur `http://localhost:5000`.

### Lancer le frontend
- Accédez au répertoire frontend et exécutez :
  ```bash
  npm run dev  # ou pnpm run dev
  ```
- L'application frontend devrait être accessible sur `http://localhost:3000`.

## Structure du projet

```
blog/
├── backend/
│   ├── app/
│   │   ├── models/              # Contient les modèles de données
│   │   │   └── post.py          # Modèle pour les articles de blog
│   │   ├── routes/              # Contient les routes de l'API
│   │   │   └── post_routes.py    # Routes pour gérer les articles
│   │   ├── config.py            # Configuration de l'application
│   │   └── main.py              # Point d'entrée de l'application
│   └── venv/                    # Environnement virtuel
└── frontend/
    ├── public/                  # Fichiers publics
    ├── src/
    │   ├── components/          # Composants réutilisables
    │   ├── pages/               # Pages de l'application
    │   │   ├── BlogDetail.jsx    # Détails d'un article
    │   │   ├── BlogList.jsx      # Liste des articles
    │   │   └── WriteBlog.jsx     # Page pour écrire un nouvel article
    │   ├── App.jsx               # Composant principal de l'application
    │   └── main.jsx              # Point d'entrée de l'application React
```

## Contribuer

Les contributions sont les bienvenues ! Pour contribuer, veuillez suivre ces étapes :
1. Forkez le projet.
2. Créez une nouvelle branche (`git checkout -b feature/YourFeature`).
3. Apportez vos modifications et validez (`git commit -m 'Ajout d'une nouvelle fonctionnalité'`).
4. Poussez vos modifications (`git push origin feature/YourFeature`).
5. Ouvrez une Pull Request.

Merci de votre intérêt pour le projet !
