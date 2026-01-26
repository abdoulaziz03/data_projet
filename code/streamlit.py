import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

st.set_page_config(page_title="Dashboard E-commerce", layout="wide")

# Chargement des données clean
@st.cache_data
def load_data():
    events_clean = pd.read_csv('../data/clean/events_clean.csv')
    category_tree_clean = pd.read_csv('../data/clean/category_tree_clean.csv')
    item_properties_clean = pd.read_csv('../data/clean/item_properties_clean.csv')
    
    # Conversion des dates si nécessaire
    if 'datetime' in events_clean.columns:
        events_clean['datetime'] = pd.to_datetime(events_clean['datetime'])
    if 'date' in events_clean.columns:
        events_clean['date'] = pd.to_datetime(events_clean['date'])
    
    return events_clean, category_tree_clean, item_properties_clean

events_clean, category_tree_clean, item_properties_clean = load_data()

st.title("📊 Dashboard Analytics E-commerce")

# ============================================================================
# 1. KPI PRINCIPAUX
# ============================================================================
st.subheader("📈 Métriques Globales")

col1, col2, col3, col4 = st.columns(4)

with col1:
    unique_users = events_clean['visitorid'].nunique()
    st.metric("👥 Utilisateurs", f"{unique_users:,}")

with col2:
    unique_products = events_clean['itemid'].nunique()
    st.metric("📦 Produits", f"{unique_products:,}")

with col3:
    purchases = events_clean.query("event=='transaction'").shape[0]
    st.metric("💰 Achats", f"{purchases:,}")

with col4:
    buyers = events_clean.query("event=='transaction'")['visitorid'].nunique()
    conversion_rate = buyers / unique_users if unique_users > 0 else 0
    st.metric("🎯 Taux Conversion", f"{conversion_rate:.2%}")

st.success("✅ Données chargées avec succès")

# ============================================================================
# 2. FUNNEL DE CONVERSION
# ============================================================================
st.subheader("🔄 Funnel de Conversion")

# Calcul des étapes du funnel
funnel_steps = {
    'Vues': events_clean.query("event=='view'").shape[0],
    'Ajouts Panier': events_clean.query("event=='addtocart'").shape[0],
    'Transactions': events_clean.query("event=='transaction'").shape[0]
}

funnel_df = pd.DataFrame({
    'Étape': list(funnel_steps.keys()),
    'Nombre': list(funnel_steps.values())
})

# Calcul des taux de conversion
funnel_df['Conversion'] = (funnel_df['Nombre'] / funnel_df['Nombre'].iloc[0] * 100).round(2)

# Affichage
col1, col2 = st.columns([3, 1])

with col1:
    # Graphique funnel
    fig = px.funnel(funnel_df, x='Nombre', y='Étape', 
                   title="Funnel de Conversion",
                   color='Étape',
                   color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c'])
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Métriques intermédiaires
    st.write("**Taux de conversion:**")
    
    view_to_cart = (funnel_steps['Ajouts Panier'] / funnel_steps['Vues'] * 100) if funnel_steps['Vues'] > 0 else 0
    cart_to_purchase = (funnel_steps['Transactions'] / funnel_steps['Ajouts Panier'] * 100) if funnel_steps['Ajouts Panier'] > 0 else 0
    
    st.metric("Vue → Panier", f"{view_to_cart:.1f}%")
    st.metric("Panier → Achat", f"{cart_to_purchase:.1f}%")
    
    # Tableau
    st.dataframe(funnel_df.style.format({'Nombre': '{:,}', 'Conversion': '{:.2f}%'}))

# ============================================================================
# 3. ACTIVITÉ TEMPORELLE
# ============================================================================
st.subheader("📅 Activité Temporelle")

# Préparation des données temporelles
if 'datetime' in events_clean.columns:
    events_clean['hour'] = events_clean['datetime'].dt.hour
    events_clean['day_of_week'] = events_clean['datetime'].dt.day_name()
    events_clean['date_only'] = events_clean['datetime'].dt.date
    
    # Sélection du type de vue
    view_option = st.radio(
        "Vue par:",
        ["Heure de la journée", "Jour de la semaine", "Date"],
        horizontal=True
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if view_option == "Heure de la journée":
            hourly_activity = events_clean.groupby('hour').size().reset_index()
            hourly_activity.columns = ['Heure', 'Activité']
            
            fig = px.bar(hourly_activity, x='Heure', y='Activité',
                        title='Activité par Heure',
                        color='Activité',
                        color_continuous_scale='blues')
            st.plotly_chart(fig, use_container_width=True)
            
            # Heure de pointe
            peak_hour = hourly_activity.loc[hourly_activity['Activité'].idxmax(), 'Heure']
            st.info(f"**Heure de pointe** : {peak_hour}h")
    
    with col2:
        if view_option == "Jour de la semaine":
            # Ordre des jours
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            day_names_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
            
            daily_activity = events_clean.groupby('day_of_week').size().reindex(day_order).reset_index()
            daily_activity.columns = ['Jour_EN', 'Activité']
            daily_activity['Jour_FR'] = day_names_fr
            
            fig = px.bar(daily_activity, x='Jour_FR', y='Activité',
                        title='Activité par Jour de Semaine',
                        color='Activité',
                        color_continuous_scale='greens')
            st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# 4. TOP PRODUITS
# ============================================================================
st.subheader("🏆 Top Produits")

# Sélection du type d'événement
event_type = st.selectbox(
    "Type d'événement:",
    ['view', 'addtocart', 'transaction'],
    format_func=lambda x: {'view': 'Vues', 'addtocart': 'Ajouts Panier', 'transaction': 'Achats'}[x]
)

# Top produits par événement
top_products = events_clean[events_clean['event'] == event_type]
top_products = top_products['itemid'].value_counts().head(10).reset_index()
top_products.columns = ['Produit', f'Nombre de {event_type}']

col1, col2 = st.columns([3, 1])

with col1:
    event_name = {'view': 'Vues', 'addtocart': 'Ajouts Panier', 'transaction': 'Achats'}[event_type]
    
    fig = px.bar(top_products, x='Produit', y=f'Nombre de {event_type}',
                title=f'Top 10 Produits par {event_name}',
                color=f'Nombre de {event_type}',
                color_continuous_scale='viridis')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.dataframe(top_products, use_container_width=True)

# ============================================================================
# 5. COMPORTEMENT UTILISATEUR
# ============================================================================
st.subheader("👤 Comportement Utilisateur")

# Distribution des sessions par utilisateur
user_sessions = events_clean.groupby('visitorid')['event'].count().reset_index()
user_sessions.columns = ['visitorid', 'sessions']

col1, col2 = st.columns(2)

with col1:
    # Histogramme des sessions
    fig = px.histogram(user_sessions, x='sessions', 
                      title='Distribution des Sessions par Utilisateur',
                      nbins=50,
                      labels={'sessions': 'Nombre de sessions', 'count': 'Nombre d\'utilisateurs'})
    fig.add_vline(x=user_sessions['sessions'].mean(), line_dash="dash", line_color="red",
                 annotation_text=f"Moyenne: {user_sessions['sessions'].mean():.1f}")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Top utilisateurs actifs
    top_users = user_sessions.nlargest(10, 'sessions')
    
    fig = px.bar(top_users, x='visitorid', y='sessions',
                title='Top 10 Utilisateurs les Plus Actifs',
                labels={'visitorid': 'ID Utilisateur', 'sessions': 'Nombre de sessions'})
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# 6. ANALYSE CATÉGORIES (si disponible)
# ============================================================================
if not category_tree_clean.empty:
    st.subheader("🌳 Analyse des Catégories")
    
    # Catégories racines
    root_categories = category_tree_clean[category_tree_clean['parentid'] == 0]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Catégories totales", len(category_tree_clean))
        st.metric("Catégories racines", len(root_categories))
    
    with col2:
        # Hiérarchie des catégories
        category_depth = {}
        for _, row in category_tree_clean.iterrows():
            depth = 1
            parent = row['parentid']
            while parent != 0 and parent in category_tree_clean['categoryid'].values:
                depth += 1
                parent = category_tree_clean[category_tree_clean['categoryid'] == parent]['parentid'].values[0]
            category_depth[row['categoryid']] = depth
        
        max_depth = max(category_depth.values()) if category_depth else 0
        st.metric("Profondeur max", max_depth)

# ============================================================================
# 7. TABS POUR APERÇU DES DONNÉES
# ============================================================================
st.subheader("📋 Aperçu des Données")

tab1, tab2, tab3 = st.tabs(["Events", "Catégories", "Propriétés"])

with tab1:
    st.write(f"**Shape:** {events_clean.shape}")
    st.dataframe(events_clean.head(100))

with tab2:
    if not category_tree_clean.empty:
        st.write(f"**Shape:** {category_tree_clean.shape}")
        st.dataframe(category_tree_clean.head(100))

with tab3:
    if not item_properties_clean.empty:
        st.write(f"**Shape:** {item_properties_clean.shape}")
        st.dataframe(item_properties_clean.head(100))

# ============================================================================
# 8. FILTRES INTERACTIFS
# ============================================================================
st.sidebar.header("🎛️ Filtres")

# Filtre par date si disponible
if 'date' in events_clean.columns:
    min_date = events_clean['date'].min()
    max_date = events_clean['date'].max()
    
    date_range = st.sidebar.date_input(
        "Période d'analyse",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    
    if len(date_range) == 2:
        filtered_events = events_clean[
            (events_clean['date'] >= pd.to_datetime(date_range[0])) &
            (events_clean['date'] <= pd.to_datetime(date_range[1]))
        ]
        st.sidebar.write(f"Événements filtrés: {len(filtered_events):,}")
    else:
        filtered_events = events_clean

# Filtre par type d'événement
event_types = events_clean['event'].unique()
selected_events = st.sidebar.multiselect(
    "Types d'événements",
    options=event_types,
    default=event_types.tolist()
)

if selected_events:
    filtered_events = events_clean[events_clean['event'].isin(selected_events)]
    st.sidebar.write(f"Événements sélectionnés: {len(filtered_events):,}")

# ============================================================================
# 9. STATISTIQUES RAPIDES
# ============================================================================
st.sidebar.header("📊 Statistiques Rapides")

if 'is_purchase' in events_clean.columns:
    total_purchases = events_clean['is_purchase'].sum()
    total_views = events_clean['is_view'].sum() if 'is_view' in events_clean.columns else 0
    
    st.sidebar.metric("Total Achats", f"{total_purchases:,}")
    st.sidebar.metric("Total Vues", f"{total_views:,}")
    
    if total_views > 0:
        conversion_rate = total_purchases / total_views * 100
        st.sidebar.metric("Taux Vue→Achat", f"{conversion_rate:.2f}%")

# ============================================================================
# 10. TÉLÉCHARGEMENT
# ============================================================================
st.sidebar.header("📥 Export")

# Bouton pour télécharger les données
@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

if st.sidebar.button("📊 Exporter les métriques"):
    metrics_df = pd.DataFrame({
        'Métrique': ['Utilisateurs uniques', 'Produits uniques', 'Total achats', 'Taux conversion'],
        'Valeur': [unique_users, unique_products, purchases, conversion_rate]
    })
    
    csv = convert_df(metrics_df)
    st.sidebar.download_button(
        label="Télécharger métriques CSV",
        data=csv,
        file_name="metrics_ecommerce.csv",
        mime="text/csv"
    )


