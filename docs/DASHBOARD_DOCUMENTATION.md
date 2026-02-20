# Documentation Complète du Dashboard E-commerce

## Table des Matières
1. [Vue d'Ensemble](#vue-densemble)
2. [Architecture Technique](#architecture-technique)
3. [Sources de Données](#sources-de-données)
4. [Composants du Dashboard](#composants-du-dashboard)
5. [Résultats d'Analyse](#résultats-danalyse)
6. [Guide d'Utilisation](#guide-dutilisation)
7. [Métriques Expliquées](#métriques-expliquées)
8. [Dépannage](#dépannage)

---

## Vue d'Ensemble

Ce document détaille toutes les fonctionnalités, métriques et visualisations du tableau de bord interactif E-Commerce développé avec Streamlit. Le tableau de bord permet d'analyser en temps réel les performances du site e-commerce et de faciliter la prise de décision basée sur les données.

### Objectifs du Dashboard
- **Visualiser les métriques clés** (KPIs) de manière claire et intuitive
- **Analyser les tendances temporelles** pour identifier les patterns et évolutions
- **Comprendre le comportement des utilisateurs** et leur parcours d'achat
- **Identifier les produits performants** et les opportunités d'optimisation
- **Faciliter la prise de décision** grâce à des visualisations interactives

---

## Architecture Technique

### Structure du Code

```
┌─────────────────────────────────────────────────────────────────┐
│                    Dashboard Streamlit                          │
├─────────────────────────────────────────────────────────────────┤
│  Page Config: page_title="Dashboard E-commerce"               │
│  Layout: wide                                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Section 1: Métriques Clés (KPIs) - 8 indicateurs         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Section 2: Visualisations Interactives (5 onglets)       │  │
│  │   - Tendances Temporelles                                │  │
│  │   - Répartition des Événements (Funnel)                  │  │
│  │   - Top Produits                                         │  │
│  │   - Analyse Horaire                                       │  │
│  │   - Comportement Utilisateurs                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Section 3: Données Détaillées                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ════════════════════════════════════════════════════════════  │
│  SIDEBAR:                                                        │
│  ┌─────────────┐  ┌─────────────┐                              │
│  │ Filtres    │  │ Options     │                              │
│  │ - Date     │  │ - Theme     │                              │
│  │ - Events   │  │ - Export    │                              │
│  └─────────────┘  └─────────────┘                              │
└─────────────────────────────────────────────────────────────────┘
```

### Fonctionnalités Techniques

#### Chargement des Données
- **Fonction `load_data()`** : Charge les données depuis les fichiers CSV
- **Fichiers recherchés** :
  - `events_clean.csv` : Contient tous les événements
  - `category_tree_clean.csv` : Contient l'arborescence des catégories
  - `item_properties_clean.csv` : Propriétés des produits
- **Fallback** : Si les fichiers ne sont pas trouvés, génère automatiquement des données de démonstration
- **Cache** : Utilise `@st.cache_data` pour optimiser les performances

#### Traitement des Données
- **Fonction `process_data()`** :
  - Convertit les timestamps en dates/heures exploitables
  - Crée des colonnes enrichies : `datetime`, `date`, `hour`, `day_of_week`, `month`, `week`

#### Design et Interface
- **En-tête** : Dégradé violet (#667eea → #764ba2)
- **Layout** : Mode "wide" pour utiliser tout l'espace disponible
- **Graphiques** : Plotly interactifs avec zoom, hover, export PNG

---

## Sources de Données

Le dashboard charge trois fichiers CSV nettoyés depuis `data/clean/`:

| Fichier | Description | Colonnes Principales |
|---------|-------------|---------------------|
| `events_clean.csv` | Événements utilisateur | visitorid, itemid, event, datetime, date |
| `category_tree_clean.csv` | Hiérarchie catégories | categoryid, parentid |
| `item_properties_clean.csv` | Propriétés produits | itemid, property, value |

### Types d'Événements
- **view** (85%) : Consultation de page produit
- **addtocart** (12%) : Ajout au panier
- **transaction** (3%) : Achat effectif

---

## Composants du Dashboard

### Section 1 : Métriques Clés (KPIs)

#### Ligne 1 : Métriques Principales

| Métrique | Description | Calcul |
|----------|-------------|--------|
| 👥 Visiteurs Uniques | Nombre total de visiteurs différents | `df['visitorid'].nunique()` |
| 🛒 Transactions | Nombre total d'achats effectués | Compte des événements 'transaction' |
| 💰 Taux de Conversion | Pourcentage de vues transformées en transactions | `(Transactions / Vues) × 100` |
| 📊 Total Événements | Nombre total d'événements | `len(df)` |

#### Ligne 2 : Métriques Détaillées

| Métrique | Description | Calcul |
|----------|-------------|--------|
| 👀 Vues | Nombre de pages produits consultées | Compte des événements 'view' |
| 🛍️ Ajouts au Panier | Nombre de produits ajoutés au panier | Compte des événements 'addtocart' |
| 🛒 Taux Panier → Transaction | % de paniers transformés en achats | `(Transactions / Ajouts) × 100` |
| 👤 Acheteurs Uniques | Visiteurs avec au moins 1 transaction | `nunique()` sur transactions |

---

### Section 2 : Visualisations Interactives (5 onglets)

#### Onglet 1 : 📈 Tendances Temporelles
- **Graphique Principal** : Évolution des événements par période (jour/semaine/mois)
- **Graphique Secondaire** : Évolution des transactions uniquement
- **Interactivité** : Zoom, pan, hover, légende cliquable

#### Onglet 2 : 🎯 Répartition des Événements
- **Graphique Camembert** : Répartition en pourcentage par type
- **Graphique en Barres** : Nombre absolu par type
- **Entonnoir de Conversion** : Vue → Panier → Transaction
- **Graphique des Taux** : Comparaison des taux de conversion

#### Onglet 3 : 🛍️ Top Produits
- **Top 20 par Vues** : Produits les plus consultés
- **Top 20 par Transactions** : Produits les plus vendus
- **Tableau Détaillé** : itemid, Vues, Transactions, Taux de Conversion

#### Onglet 4 : ⏰ Analyse Horaire
- **Événements par Heure** : Distribution 0-23h
- **Événements par Jour** : Distribution lundi-dimanche
- **Heatmap** : Croisement Heure × Jour

#### Onglet 5 : 👥 Comportement Utilisateurs
- **Histogramme** : Distribution des événements par visiteur
- **Camembert** : Répartition par niveau d'activité
- **Top 20 Visiteurs** : Utilisateurs les plus actifs
- **Analyse des Acheteurs** : Métriques clients

---

### Section 3 : Données Détaillées
- **Tableau des Données Brutes** : 1000 premières lignes
- **Statistiques Descriptives** : Moyenne, écart-type, quartiles

---

## Résultats d'Analyse

### Métriques Clés du Dataset

| Métrique | Valeur | Description |
|----------|--------|-------------|
| **Total Événements** | ~2,756,101 | Nombre total d'événements utilisateur |
| **Visiteurs Uniques** | ~1,407,580 | Nombre de visiteurs différents |
| **Produits Catalogués** | ~235,061 | Nombre de produits dans le catalogue |
| **Transactions** | ~11,359 | Nombre d'achats effectués |
| **Période** | Mai-Juillet 2015 | Dates des données |

### Funnel de Conversion

```
┌─────────────────────────────────────────────────────────┐
│                    FUNNEL DE CONVERSION                  │
├─────────────────────────────────────────────────────────┤
│   ┌─────────────┐                                        │
│   │    VUES     │  ← 2,756,101 (100%)                    │
│   └──────┬──────┘                                        │
│          │ ~3.5%                                         │
│   ┌──────▼──────┐                                        │
│   │   AJOUTS    │  ← ~96,463 (3.5%)                       │
│   │   PANIER    │                                        │
│   └──────┬──────┘                                        │
│          │ ~11.8%                                         │
│   ┌──────▼──────┐                                        │
│   │  TRANSACT.  │  ← ~11,359 (0.41%)                     │
│   └─────────────┘                                        │
└─────────────────────────────────────────────────────────┘
```

### Taux de Conversion

| Étape | Taux | Interprétation |
|-------|------|----------------|
| Vue → Panier | ~3.5% | Faible - Optimiser les fiches produits |
| Panier → Transaction | ~11.8% | Moyen - Réduire les abandons de panier |
| Vue → Transaction | ~0.41% | Taux global de conversion |

### Analyse Temporelle

| Métrique | Valeur | Insight |
|----------|--------|---------|
| **Heure de Pointe** | 20h | Peak d'activité en soirée |
| **Jour le Plus Actif** | Vendredi | Week-end précédent |
| **Sessions/Visiteur** | ~2.0 | Comportement moyen |

### Segmentation Client

| Segment | Description |
|---------|-------------|
| **Champions** | Clients récents, fréquents et à forte valeur |
| **Nouveaux Clients** | Récemment acquis |
| **Clients à Risque** | Anciens clients inactifs |
| **Clients Perdus** | Inactifs depuis longtemps |

### Top Produits Types
- **Par Vues** : Produits populaires à forte exposition
- **Par Transactions** : Best-sellers à promouvoir
- **À Optimiser** : Produits à forte vue mais faible conversion

---

## Guide d'Utilisation

### Lancement du Dashboard

```
bash
# Méthode 1: Depuis la racine du projet
streamlit run code/streamlit.py

# Méthode 2: Depuis le dossier code
cd code
streamlit run streamlit.py
```

**URL d'accès** : `http://localhost:8501`

### Navigation

1. **En-tête** : Vue d'ensemble et titre
2. **Sidebar** : Filtres et options (masquable)
3. **Corps principal** :
   - Section 1 : Métriques clés
   - Section 2 : Visualisations (5 onglets)
   - Section 3 : Données détaillées

### Utilisation des Filtres

#### Filtre Temporel
1. Dans la sidebar, cliquez sur **Période d'analyse**
2. Sélectionnez la date de début et de fin
3. Toutes les visualisations se mettent à jour

#### Filtre par Type d'Événement
1. Dans la sidebar, cliquez sur **Types d'événements**
2. Cochez/décochez : view, addtocart, transaction
3. Les données sont filtrées automatiquement

### Export des Données
1. Cliquez sur **Exporter les données** dans la sidebar
2. Téléchargement automatique en CSV

---

## Métriques Expliquées

### Formules de Calcul

#### Taux de Conversion Vue → Transaction
```
Taux = (Transactions / Vues) × 100
```

#### Taux de Conversion Vue → Panier
```
Taux = (Ajouts Panier / Vues) × 100
```

#### Taux de Conversion Panier → Transaction
```
Taux = (Transactions / Ajouts Panier) × 100
```

#### Taux d'Achat (Buyer Rate)
```
Taux = (Acheteurs Uniques / Visiteurs Uniques) × 100
```

#### Moyenne d'Événements par Visiteur
```
Moyenne = Total Événements / Visiteurs Uniques
```

### Seils d'Alerte

| Métrique | Seuil Alarmant | Action Recommandée |
|----------|----------------|-------------------|
| Vue→Panier | < 2% | Optimiser fiches produits |
| Panier→Transaction | < 5% | Réduire abandons panier |
| Sessions/Utilisateur | < 1.5 | Améliorer engagement |

---

## Dépannage

### Problèmes Courants

#### 1. Données non chargées
**Symptôme** : Messages d'erreur sur les fichiers
**Solution** : Vérifier les chemins dans `data/clean/`

#### 2. Graphiques vides
**Symptôme** : visualisations sans données
**Solution** : Vérifier les filtres (peuvent tout exclure)

#### 3. Performance lente
**Solution** : 
- Vider le cache : `Ctrl+C` puis relancer
- Pour >1M lignes : considérer l'échantillonnage

#### 4. Erreurs d'affichage
**Solution** : 
- Vérifier Python 3.8+
- Installer dépendances : `pip install -r requirements.txt`

### Dépendances Requises
- `streamlit` >= 1.20.0
- `pandas` >= 1.5.0
- `numpy` >= 1.23.0
- `plotly` >= 5.14.0

---

## Cas d'Usage

### 1. Analyse Quotidienne
1. Filtrer sur la date du jour
2. Consulter les KPIs principaux
3. Vérifier les tendances temporelles
4. Examiner le top produits

### 2. Analyse de Campagne
1. Filtrer sur la période de la campagne
2. Comparer avec la période précédente
3. Analyser l'évolution des conversions

### 3. Identification de Problèmes
1. Examiner l'entonnoir de conversion
2. Identifier où se perdent les clients
3. Analyser les produits à forte vue mais faible vente

### 4. Planification Stratégique
1. Analyser les patterns horaires/hebdomadaires
2. Identifier les heures/jours de pointe
3. Planifier les campagnes et le staffing

---


