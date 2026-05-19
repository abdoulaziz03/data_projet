# E-Commerce Analytics Dashboard (RetailRocket)

Un projet complet d’analyse de données e-commerce utilisant le dataset **RetailRocket** pour :
- comprendre le comportement utilisateur,
- construire des métriques clés (conversion, funnel, temporalité),
- segmenter les clients (RFM),
- évaluer des **tests A/B**,
- présenter le tout dans un **dashboard interactif** via Streamlit.

---

## Aperçu (Screenshots)

![Dashboard Overview](./images/image1.png)

![Dashboard : Insights / Graphiques](./images/imagedsh1.png)

---

## Fonctionnalités

### Analyse de données
- **Métriques globales** : utilisateurs uniques, produits, transactions, taux de conversion
- **Funnel de conversion** : vue → panier → achat
- **Analyse temporelle** : activité par heure et par jour de semaine
- **Segmentation RFM** : Récence, Fréquence, Montant
- **Analyse des abandons** : produits fréquemment abandonnés dans le panier

### Tests A/B
- **Test global** : comparaison des performances A vs B
- **Tests par catégorie** : impact sur grandes et sous-catégories
- **Tests temporels** : performance selon l’heure et le jour
- **Analyse UX** : évaluation des parcours utilisateur

### Dashboard interactif
- **KPIs** et visualisations **Plotly** interactives
- **Filtres dynamiques** (période, type d’événement, segments)
- **Exploration** des données nettoyées
- **Export** des résultats

---

## Technologies utilisées

- **Python**
- **Pandas**
- **Streamlit**
- **Plotly**
- **MongoDB**
- **Jupyter Notebook**
- **SciPy / Statsmodels** (statistiques & tests A/B)

---

## Installation

### Prérequis
- Python **3.8+**
- MongoDB (local ou cloud)
- Git

### Étapes

1) **Cloner le repository**
```bash
git clone <https://github.com/abdoulaziz03/data_projet.git>
cd data_projet
```

2) **Créer un environnement virtuel**
```bash
python -m venv venv
venv\Scripts\activate
```

3) **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4) **Configurer MongoDB**
Créer un fichier **`.env`** à la racine :
```env
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=votre_base_donnees
```

---

## Démarrage & Utilisation

### 1) Préparation des données
Lancer le notebook de traitement des données :
```bash
jupyter notebook Notebook/traitement.ipynb
```

Ce notebook effectue :
- chargement des données brutes
- nettoyage & transformation
- analyses exploratoires
- segmentation RFM
- sauvegarde des datasets nettoyés

### 2) Tests A/B
Lancer l’analyse A/B :
```bash
jupyter notebook Notebook/ABtesting.ipynb
```

Analyses disponibles :
- tests globaux
- tests par catégorie
- tests temporels
- analyse des abandons

### 3) Dashboard Streamlit
```bash
streamlit run code/streamlit.py
```

Accéder à : `http://localhost:8501`

### 4) Intégration MongoDB
```bash
python data_collection/insertion_versmongo.py
```

---

## Structure du projet

```text
data_projet/
├── code/
│   └── streamlit.py                 # Dashboard principal
├── data/
│   ├── raw/                         # Données brutes
│   │   ├── events.csv
│   │   ├── category_tree.csv
│   │   └── item_properties_part1.csv
│   └── clean/                       # Données nettoyées
│       ├── events_clean.csv
│       ├── category_tree_clean.csv
│       └── item_properties_clean.csv
├── data_collection/
│   └── insertion_versmongo.py      # Script MongoDB
├── Notebook/
│   ├── traitement.ipynb            # Analyse et nettoyage
│   └── ABtesting.ipynb             # Tests A/B
├── config/                          # Configuration
├── docs/                            # Documentation
├── src/                             # Code source additionnel
├── .env                             # Variables d’environnement
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Jeu de données

Le projet utilise **RetailRocket E-commerce** :
- **Events** : événements utilisateur (vues, ajouts panier, achats)
- **Category Tree** : hiérarchie des catégories
- **Item Properties** : propriétés détaillées des produits

### Repères (ordre de grandeur)
- 2,756,101 événements utilisateur
- 1,407,580 visiteurs uniques
- 235,061 produits catalogués
- 11,359 transactions
- Période : mai → juillet 2015

---

## Contribution

1. Fork le projet
2. Créer une branche :
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. Commit :
   ```bash
   git commit -m "Add some AmazingFeature"
   ```
4. Push :
   ```bash
   git push origin feature/AmazingFeature
   ```
5. Ouvrir une Pull Request

---

## Licence

Ce projet est sous licence **MIT**. Voir le fichier `LICENSE`.

---

## Remerciements

- Dataset : [RetailRocket](https://www.kaggle.com/retailrocket/ecommerce-dataset)
- Communauté **Streamlit** et bibliothèques open-source

---

## Auteur

**Touré Abdoul-aziz**


