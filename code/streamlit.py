import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configuration
st.set_page_config(
    page_title="Dashboard E-commerce",
    page_icon="📊",
    layout="wide"
)

# Chargement des données
@st.cache_data
def load_data():
    events_clean = pd.read_csv('../data/clean/events_clean.csv')
    category_tree_clean = pd.read_csv('../data/clean/category_tree_clean.csv')
    item_properties_clean = pd.read_csv('../data/clean/item_properties_clean.csv')
    
    # Conversion des dates si nécessaire
    if 'timestamp' in events_clean.columns:
        events_clean['timestamp'] = pd.to_datetime(events_clean['timestamp'])
    
    return events_clean, category_tree_clean, item_properties_clean

# Titre
st.title("📊 Tableau de Bord E-commerce")
st.markdown("---")

# Sidebar pour la navigation
st.sidebar.title("Navigation")
option = st.sidebar.selectbox(
    "Choisir une analyse:",
    [
        "Vue d'ensemble",
        "Funnel de conversion", 
        "Top produits",
        "Activité temporelle",
        "Comportement utilisateur",
        "Analyse RFM",
        "Abandons panier"
    ]
)

# Chargement des données
with st.spinner('Chargement des données...'):
    try:
        events, categories, properties = load_data()
        st.sidebar.success("✅ Données chargées")
    except:
        st.error("Erreur de chargement des données")
        st.stop()

# 1. VUE D'ENSEMBLE
if option == "Vue d'ensemble":
    st.header("📈 Vue d'ensemble")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_events = len(events)
        st.metric("Total événements", f"{total_events:,}")
    
    with col2:
        total_visitors = events['visitorid'].nunique() if 'visitorid' in events.columns else "N/A"
        st.metric("Visiteurs uniques", f"{total_visitors:,}")
    
    with col3:
        total_products = events['itemid'].nunique() if 'itemid' in events.columns else "N/A"
        st.metric("Produits uniques", f"{total_products:,}")
    
    with col4:
        total_categories = len(categories) if 'categories' in locals() else "N/A"
        st.metric("Catégories", f"{total_categories:,}")
    
    # Distribution des événements
    st.subheader("Distribution des événements")
    if 'event' in events.columns:
        event_counts = events['event'].value_counts()
        fig = px.pie(values=event_counts.values, names=event_counts.index, title="Types d'événements")
        st.plotly_chart(fig, use_container_width=True)
    
    # Aperçu des données
    st.subheader("Aperçu des données")
    tab1, tab2, tab3 = st.tabs(["Événements", "Catégories", "Propriétés"])
    
    with tab1:
        st.dataframe(events.head(100))
        st.caption(f"Shape: {events.shape}")
    
    with tab2:
        st.dataframe(categories.head(100))
        st.caption(f"Shape: {categories.shape}")
    
    with tab3:
        st.dataframe(properties.head(100))
        st.caption(f"Shape: {properties.shape}")

# 2. FUNNEL DE CONVERSION
elif option == "Funnel de conversion":
    st.header("🛒 Funnel de conversion")
    
    if 'event' in events.columns:
        # Calcul des étapes du funnel
        views = len(events[events['event'] == 'view'])
        cart_adds = len(events[events['event'] == 'addtocart'])
        transactions = len(events[events['event'] == 'transaction'])
        
        # Métriques
        col1, col2, col3 = st.columns(3)
        
        with col1:
            conversion_rate = (transactions / views * 100) if views > 0 else 0
            st.metric("Taux de conversion", f"{conversion_rate:.2f}%")
        
        with col2:
            cart_rate = (cart_adds / views * 100) if views > 0 else 0
            st.metric("Taux d'ajout panier", f"{cart_rate:.2f}%")
        
        with col3:
            purchase_rate = (transactions / cart_adds * 100) if cart_adds > 0 else 0
            st.metric("Taux de conversion panier", f"{purchase_rate:.2f}%")
        
        # Funnel visuel
        st.subheader("Funnel de conversion")
        
        funnel_data = pd.DataFrame({
            'Étape': ['Vues', 'Ajouts panier', 'Transactions'],
            'Nombre': [views, cart_adds, transactions],
            'Pourcentage': [100, (cart_adds/views*100) if views>0 else 0, (transactions/views*100) if views>0 else 0]
        })
        
        fig = go.Figure(go.Funnel(
            y=funnel_data['Étape'],
            x=funnel_data['Nombre'],
            textinfo="value+percent initial"
        ))
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Tableau détaillé
        st.dataframe(funnel_data)

# 3. TOP PRODUITS
elif option == "Top produits":
    st.header("🔥 Top produits")
    
    if 'itemid' in events.columns and 'event' in events.columns:
        # Sélecteur de type
        metric_type = st.selectbox(
            "Choisir la métrique:",
            ["Les plus vus", "Les plus ajoutés au panier", "Les plus vendus"]
        )
        
        if metric_type == "Les plus vus":
            top_products = events[events['event'] == 'view'].groupby('itemid').size().reset_index(name='vues')
            top_products = top_products.sort_values('vues', ascending=False).head(20)
            title = "Top 20 produits les plus vus"
            col_name = 'vues'
        
        elif metric_type == "Les plus ajoutés au panier":
            top_products = events[events['event'] == 'addtocart'].groupby('itemid').size().reset_index(name='ajouts_panier')
            top_products = top_products.sort_values('ajouts_panier', ascending=False).head(20)
            title = "Top 20 produits les plus ajoutés au panier"
            col_name = 'ajouts_panier'
        
        else:  # Les plus vendus
            top_products = events[events['event'] == 'transaction'].groupby('itemid').size().reset_index(name='ventes')
            top_products = top_products.sort_values('ventes', ascending=False).head(20)
            title = "Top 20 produits les plus vendus"
            col_name = 'ventes'
        
        # Graphique
        fig = px.bar(
            top_products.head(10),
            x=col_name,
            y='itemid',
            orientation='h',
            title=title,
            color=col_name
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Tableau complet
        st.dataframe(top_products)

# 4. ACTIVITÉ TEMPORELLE
elif option == "Activité temporelle":
    st.header("⏰ Activité temporelle")
    
    if 'hour' in events.columns and 'day_of_week' in events.columns:
        # ANALYSE PAR HEURE
        st.subheader("📊 Analyse par heure")
        
        activite_horaire = events.groupby('hour').size().reset_index(name='count')
        activite_horaire = activite_horaire.sort_values('hour')
        
        if not activite_horaire.empty:
            # Trouver l'heure de pointe
            heure_pointe = activite_horaire.loc[activite_horaire['count'].idxmax(), 'hour']
            max_events = activite_horaire.loc[activite_horaire['count'].idxmax(), 'count']
            
            # Créer le graphique d'activité par heure
            fig_heure = go.Figure()
            
            # Ajouter la ligne principale
            fig_heure.add_trace(go.Scatter(
                x=activite_horaire['hour'],
                y=activite_horaire['count'],
                mode='lines+markers',
                line=dict(color='#9b59b6', width=2),
                marker=dict(size=6, color='#9b59b6'),
                name='Événements'
            ))
            
            # Ajouter une ligne verticale pour l'heure de pointe
            fig_heure.add_vline(
                x=heure_pointe,
                line_dash="dash",
                line_color="red",
                opacity=0.7
            )
            
            # Ajouter annotation pour l'heure de pointe
            fig_heure.add_annotation(
                x=heure_pointe,
                y=max_events * 0.9,
                text=f'Pic: {heure_pointe}h',
                showarrow=True,
                arrowhead=2,
                arrowcolor="red",
                font=dict(color="red", size=12, weight="bold"),
                bgcolor="white"
            )
            
            # Mise en forme du graphique
            fig_heure.update_layout(
                title="ACTIVITÉ PAR HEURE",
                title_font=dict(size=16, weight="bold"),
                xaxis_title="Heure de la Journée",
                yaxis_title="Nombre d'Événements",
                plot_bgcolor='white',
                hovermode='x',
                xaxis=dict(
                    gridcolor='rgba(0,0,0,0.1)',
                    tickmode='linear',
                    dtick=1
                ),
                yaxis=dict(
                    gridcolor='rgba(0,0,0,0.1)'
                )
            )
            
            # Afficher le graphique
            st.plotly_chart(fig_heure, use_container_width=True)
            
            # ANALYSE PAR JOUR DE SEMAINE
            st.subheader("📅 Analyse par jour de semaine")
            
            # S'assurer que les jours sont dans le bon ordre
            jours_ordre = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            # Traduction des jours si nécessaire
            jours_fr = {
                'Monday': 'Lundi',
                'Tuesday': 'Mardi', 
                'Wednesday': 'Mercredi',
                'Thursday': 'Jeudi',
                'Friday': 'Vendredi',
                'Saturday': 'Samedi',
                'Sunday': 'Dimanche'
            }
            
            activite_jour_semaine = events.groupby('day_of_week').size().reset_index(name='count')
            
            # Réindexer selon l'ordre des jours
            activite_jour_semaine['day_of_week'] = pd.Categorical(
                activite_jour_semaine['day_of_week'], 
                categories=jours_ordre, 
                ordered=True
            )
            activite_jour_semaine = activite_jour_semaine.sort_values('day_of_week')
            
            # Créer le graphique en barres
            fig_jour = go.Figure()
            
            fig_jour.add_trace(go.Bar(
                x=[jours_fr.get(jour, jour) for jour in activite_jour_semaine['day_of_week']],
                y=activite_jour_semaine['count'],
                marker_color='lightseagreen',
                opacity=0.8,
                text=activite_jour_semaine['count'],
                texttemplate='%{text:,}',
                textposition='outside'
            ))
            
            # Mise en forme du graphique
            fig_jour.update_layout(
                title="ACTIVITÉ PAR JOUR DE SEMAINE",
                title_font=dict(size=16, weight="bold"),
                xaxis_title="Jour de Semaine",
                yaxis_title="Nombre d'Événements",
                plot_bgcolor='white',
                xaxis=dict(
                    tickangle=-45
                ),
                yaxis=dict(
                    gridcolor='rgba(0,0,0,0.1)'
                )
            )
            
            # Afficher le graphique
            st.plotly_chart(fig_jour, use_container_width=True)
            
            # AFFICHAGE DES MÉTRIQUES
            st.subheader("📈 Métriques clés")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    label="Heure de pointe",
                    value=f"{heure_pointe}:00",
                    delta=f"{max_events:,} événements"
                )
            
            with col2:
                jour_pointe = activite_jour_semaine.loc[activite_jour_semaine['count'].idxmax(), 'day_of_week']
                jour_pointe_count = activite_jour_semaine.loc[activite_jour_semaine['count'].idxmax(), 'count']
                jour_fr = jours_fr.get(str(jour_pointe), jour_pointe)
                st.metric(
                    label="Jour le plus actif",
                    value=jour_fr,
                    delta=f"{jour_pointe_count:,} événements"
                )
            
            with col3:
                total_events = activite_horaire['count'].sum()
                avg_per_hour = total_events / 24
                st.metric(
                    label="Moyenne par heure",
                    value=f"{avg_per_hour:,.0f}",
                    delta=f"Total: {total_events:,}"
                )
            
            # TABLEAU DE DONNÉES DÉTAILLÉES
            with st.expander("📋 Voir les données détaillées"):
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.write("**Par heure (top 10)**")
                    top_heures = activite_horaire.sort_values('count', ascending=False).head(10)
                    top_heures['% du total'] = (top_heures['count'] / total_events * 100).round(2)
                    st.dataframe(top_heures)
                
                with col_b:
                    st.write("**Par jour de semaine**")
                    activite_jour_semaine['% du total'] = (activite_jour_semaine['count'] / total_events * 100).round(2)
                    activite_jour_semaine['Jour'] = [jours_fr.get(j, j) for j in activite_jour_semaine['day_of_week']]
                    st.dataframe(activite_jour_semaine[['Jour', 'count', '% du total']])
            
            # ANALYSE HEURE × JOUR (HEATMAP)
            st.subheader("🌅 Heatmap: Heure × Jour")
            
            try:
                # Créer une matrice heure x jour
                heatmap_data = events.groupby(['day_of_week', 'hour']).size().reset_index(name='count')
                
                if not heatmap_data.empty:
                    # Préparer les données
                    heatmap_data['day_of_week'] = pd.Categorical(
                        heatmap_data['day_of_week'], 
                        categories=jours_ordre, 
                        ordered=True
                    )
                    heatmap_data = heatmap_data.sort_values(['day_of_week', 'hour'])
                    
                    # Pivoter pour la heatmap
                    pivot_data = heatmap_data.pivot_table(
                        index='hour', 
                        columns='day_of_week', 
                        values='count', 
                        aggfunc='sum', 
                        fill_value=0
                    )
                    
                    # Réorganiser les colonnes
                    pivot_data = pivot_data.reindex(columns=jours_ordre)
                    
                    # Créer la heatmap
                    fig_heatmap = px.imshow(
                        pivot_data,
                        labels=dict(
                            x="Jour de la semaine", 
                            y="Heure", 
                            color="Événements"
                        ),
                        title="Distribution horaire par jour de semaine",
                        color_continuous_scale='YlOrRd',
                        aspect='auto'
                    )
                    
                    # Personnaliser la heatmap
                    fig_heatmap.update_xaxes(
                        ticktext=[jours_fr.get(j, j) for j in jours_ordre],
                        tickvals=jours_ordre,
                        side="top"
                    )
                    
                    fig_heatmap.update_layout(
                        height=500
                    )
                    
                    st.plotly_chart(fig_heatmap, use_container_width=True)
                    
                    # Trouver la période la plus active
                    max_period = heatmap_data.loc[heatmap_data['count'].idxmax()]
                    max_day_fr = jours_fr.get(str(max_period['day_of_week']), max_period['day_of_week'])
                    
                    st.success(
                        f"**Période la plus active** : {max_day_fr} à {int(max_period['hour'])}:00 "
                        f"({max_period['count']:,} événements)"
                    )
            except Exception as e:
                st.warning(f"Impossible de créer la heatmap : {e}")
        
        else:
            st.warning("Aucune donnée disponible pour l'analyse temporelle")
    
    else:
        st.warning("⚠️ Les colonnes 'hour' et/ou 'day_of_week' ne sont pas disponibles")
        
        # Alternative: essayer de les créer à partir de timestamp
        if 'timestamp' in events.columns:
            st.info("Tentative d'extraction des informations temporelles...")
            
            try:
                events['hour'] = events['timestamp'].dt.hour
                events['day_of_week'] = events['timestamp'].dt.day_name()
                
                # Réessayer avec les nouvelles colonnes
                st.experimental_rerun()
            except:
                st.error("Impossible d'extraire les informations temporelles du timestamp")

# 5. COMPORTEMENT UTILISATEUR
elif option == "Comportement utilisateur":
    st.header("👤 Comportement Utilisateur")
    
    if 'visitorid' in events.columns:
        # Distribution des sessions par visiteur
        sessions_par_visiteur = events.groupby('visitorid').size()
        
        # Vérifier si la colonne is_purchase existe
        has_purchase_col = 'is_purchase' in events.columns
        
        # LAYOUT PRINCIPAL - 3 COLONNES
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("📊 Distribution des Sessions")
            
            # Prendre les 95% premiers pour mieux voir la distribution
            sessions_filtre = sessions_par_visiteur[sessions_par_visiteur <= sessions_par_visiteur.quantile(0.95)]
            
            # Créer l'histogramme
            fig_hist = go.Figure()
            
            fig_hist.add_trace(go.Histogram(
                x=sessions_filtre.values,
                nbinsx=30,
                marker_color='#3498db',
                opacity=0.7,
                name='Visiteurs'
            ))
            
            # Ajouter ligne de la moyenne
            moyenne = sessions_par_visiteur.mean()
            fig_hist.add_vline(
                x=moyenne,
                line_dash="dash",
                line_color="red",
                line_width=2,
                annotation_text=f"Moyenne: {moyenne:.2f}",
                annotation_position="top right"
            )
            
            fig_hist.update_layout(
                title='DISTRIBUTION DES SESSIONS par Visiteur',
                title_font=dict(size=14, weight="bold"),
                xaxis_title='Nombre de Sessions',
                yaxis_title='Nombre de Visiteurs',
                plot_bgcolor='white',
                bargap=0.1,
                showlegend=False
            )
            
            fig_hist.update_xaxes(gridcolor='rgba(0,0,0,0.1)')
            fig_hist.update_yaxes(gridcolor='rgba(0,0,0,0.1)')
            
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            st.subheader("🏆 Top 10 Visiteurs Actifs")
            
            # Top 10 visiteurs
            top_visiteurs = sessions_par_visiteur.nlargest(10).reset_index()
            top_visiteurs.columns = ['visitorid', 'sessions']
            
            # Créer des labels pour l'affichage
            top_visiteurs['label'] = ['Visiteur ' + str(v) for v in top_visiteurs['visitorid']]
            
            fig_bar = go.Figure()
            
            fig_bar.add_trace(go.Bar(
                y=top_visiteurs['label'],
                x=top_visiteurs['sessions'],
                orientation='h',
                marker_color='#e74c3c',
                opacity=0.8,
                text=top_visiteurs['sessions'].astype(str) + ' sessions',
                textposition='outside',
                textfont=dict(size=10, weight="bold")
            ))
            
            fig_bar.update_layout(
                title='TOP 10 VISITEURS LES PLUS ACTIFS',
                title_font=dict(size=14, weight="bold"),
                xaxis_title='Nombre de Sessions',
                plot_bgcolor='white',
                height=400,
                yaxis=dict(autorange="reversed")
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col3:
            st.subheader("🎯 Répartition par Comportement")
            
            # Catégoriser les visiteurs
            visiteurs_one_shot = (sessions_par_visiteur == 1).sum()
            visiteurs_occasionnels = ((sessions_par_visiteur > 1) & (sessions_par_visiteur <= 5)).sum()
            visiteurs_reguliers = ((sessions_par_visiteur > 5) & (sessions_par_visiteur <= 20)).sum()
            visiteurs_fideles = (sessions_par_visiteur > 20).sum()
            
            categories_visiteurs = {
                'One-shot (1 session)': visiteurs_one_shot,
                'Occasionnels (2-5 sessions)': visiteurs_occasionnels,
                'Réguliers (6-20 sessions)': visiteurs_reguliers,
                'Fidèles (>20 sessions)': visiteurs_fideles
            }
            
            # Créer le camembert
            fig_pie = go.Figure()
            
            fig_pie.add_trace(go.Pie(
                labels=list(categories_visiteurs.keys()),
                values=list(categories_visiteurs.values()),
                hole=0.3,
                marker_colors=['#95a5a6', '#3498db', '#9b59b6', '#e74c3c'],
                textinfo='percent+label',
                textposition='outside',
                insidetextorientation='radial'
            ))
            
            fig_pie.update_layout(
                title='REPARTITION DES VISITEURS par Type de Comportement',
                title_font=dict(size=14, weight="bold"),
                showlegend=False,
                height=400
            )
            
            st.plotly_chart(fig_pie, use_container_width=True)
        
        # ANALYSE AVANCÉE
        st.subheader("📈 Analyse Comportementale Avancée")
        
        if has_purchase_col:
            # Visiteurs avec achat vs sans achat
            visiteurs_avec_achat = events[events['is_purchase'] == 1]['visitorid'].nunique()
            total_visitors = sessions_par_visiteur.shape[0]
            visiteurs_sans_achat = total_visitors - visiteurs_avec_achat
            
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                pct_avec = (visiteurs_avec_achat / total_visitors * 100) if total_visitors > 0 else 0
                st.metric(
                    "Visiteurs avec achat",
                    f"{visiteurs_avec_achat:,}",
                    delta=f"{pct_avec:.1f}%"
                )
            
            with col_b:
                pct_sans = (visiteurs_sans_achat / total_visitors * 100) if total_visitors > 0 else 0
                st.metric(
                    "Visiteurs sans achat",
                    f"{visiteurs_sans_achat:,}",
                    delta=f"{pct_sans:.1f}%"
                )
            
            with col_c:
                # Sessions moyennes par type
                sessions_acheteurs = events[events['is_purchase'] == 1].groupby('visitorid').size()
                sessions_non_acheteurs = events[events['is_purchase'] == 0].groupby('visitorid').size()
                
                avg_acheteurs = sessions_acheteurs.mean() if len(sessions_acheteurs) > 0 else 0
                avg_non_acheteurs = sessions_non_acheteurs.mean() if len(sessions_non_acheteurs) > 0 else 0
                
                st.metric(
                    "Différence sessions moyennes",
                    f"{avg_acheteurs:.1f} vs {avg_non_acheteurs:.1f}",
                    delta=f"{avg_acheteurs - avg_non_acheteurs:.1f}"
                )
    
        
# 6. ANALYSE RFM
elif option == "Analyse RFM":
    st.header("🎯 Segmentation RFM - Clients Acheteurs")
    
    if 'visitorid' in events.columns and 'event' in events.columns and 'timestamp' in events.columns:
        # Filtrer les transactions
        transactions = events[events['event'] == 'transaction']
        
        if len(transactions) > 0:
            # Calcul RFM de base
            reference_date = transactions['timestamp'].max()
            
            rfm = transactions.groupby('visitorid').agg({
                'timestamp': lambda x: (reference_date - x.max()).days,
                'itemid': 'count'
            }).reset_index()
            
            rfm.columns = ['visitorid', 'recency', 'frequency']
            
            # AJOUTER IMPORT numpy
            import numpy as np
            
            # A. ANALYSE DES DONNÉES
            st.subheader("📊 Analyse des données RFM")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Clients acheteurs", f"{len(rfm):,}")
                st.caption("Sur 11,719 clients")
            
            with col2:
                recency_val = rfm['recency'].iloc[0] if len(rfm) > 0 else 0
                st.metric("Recency unique", f"{recency_val} jours")
                st.caption("Tous les clients ont la même valeur")
            
            with col3:
                avg_freq = rfm['frequency'].mean()
                st.metric("Fréquence moyenne", f"{avg_freq:.1f}")
                st.caption("Par client")
            
            with col4:
                max_freq = rfm['frequency'].max()
                st.metric("Fréquence max", max_freq)
                st.caption("Client le plus actif")
            
            # B. EXPLICATION DU PROBLÈME
            st.info("""
            **Analyse des données:**
            - Tous les clients ont le **même recency** (dernier achat à la même date)
            - **76 niveaux différents de fréquence d'achat**
            - La segmentation sera basée uniquement sur la fréquence
            """)
            
            # C. SEGMENTATION BASÉE SUR LA FRÉQUENCE SEULEMENT
            st.subheader("🏷️ Segmentation par Fréquence d'Achat")
            
            # Analyser la distribution de la fréquence
            frequency_stats = rfm['frequency'].describe()
            st.write("**Distribution de la fréquence:**")
            st.write(frequency_stats)
            
            # Méthode robuste pour segmenter la fréquence
            # Utiliser des percentiles adaptatifs
            percentiles = [25, 50, 75, 90, 95]
            percentile_values = np.percentile(rfm['frequency'], percentiles)
            
            st.write("**Percentiles de fréquence:**")
            for p, val in zip(percentiles, percentile_values):
                st.write(f"- {p}% des clients ont ≤ {val:.1f} achats")
            
            # Segmentation en 5 groupes basés sur la fréquence
            def segment_by_frequency(freq):
                if freq <= percentile_values[0]:  # ≤ 25e percentile
                    return 'Acheteurs occasionnels'
                elif freq <= percentile_values[1]:  # ≤ 50e percentile (médiane)
                    return 'Acheteurs réguliers'
                elif freq <= percentile_values[2]:  # ≤ 75e percentile
                    return 'Acheteurs fréquents'
                elif freq <= percentile_values[3]:  # ≤ 90e percentile
                    return 'Acheteurs très fréquents'
                else:  # Top 10%
                    return 'Clients VIP'
            
            rfm['Segment'] = rfm['frequency'].apply(segment_by_frequency)
            
            # D. VISUALISATIONS
            col1, col2 = st.columns(2)
            
            with col1:
                # Distribution des segments
                segment_dist = rfm['Segment'].value_counts().reset_index()
                segment_dist.columns = ['Segment', 'Nombre']
                
                # Ordonner les segments logiquement
                segment_order = ['Acheteurs occasionnels', 'Acheteurs réguliers', 
                               'Acheteurs fréquents', 'Acheteurs très fréquents', 'Clients VIP']
                segment_dist['Segment'] = pd.Categorical(segment_dist['Segment'], 
                                                       categories=segment_order, 
                                                       ordered=True)
                segment_dist = segment_dist.sort_values('Segment')
                
                fig = px.bar(segment_dist, x='Segment', y='Nombre',
                            title="Distribution des Clients par Fréquence d'Achat",
                            color='Nombre',
                            text='Nombre',
                            color_continuous_scale='viridis')
                fig.update_traces(texttemplate='%{text:,}', textposition='outside')
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Histogramme de la fréquence
                fig = px.histogram(rfm, x='frequency', nbins=30,
                                  title="Distribution de la Fréquence d'Achat",
                                  labels={'frequency': 'Nombre d\'achats'},
                                  color_discrete_sequence=['#636EFA'])
                fig.update_layout(bargap=0.1)
                st.plotly_chart(fig, use_container_width=True)
                
                # Ajouter des lignes pour les percentiles
                fig.add_vline(x=percentile_values[0], line_dash="dash", line_color="red",
                            annotation_text="25%", annotation_position="top")
                fig.add_vline(x=percentile_values[1], line_dash="dash", line_color="orange",
                            annotation_text="50%", annotation_position="top")
                fig.add_vline(x=percentile_values[2], line_dash="dash", line_color="green",
                            annotation_text="75%", annotation_position="top")
            
            # E. STATISTIQUES PAR SEGMENT
            st.subheader("📈 Statistiques détaillées par Segment")
            
            segment_stats = rfm.groupby('Segment').agg({
                'frequency': ['count', 'mean', 'min', 'max', 'sum'],
                'visitorid': 'nunique'
            }).round(2)
            
            segment_stats.columns = ['Nb_Clients', 'Freq_Moyenne', 'Freq_Min', 'Freq_Max', 'Total_Achats', 'Clients_Uniques']
            
            # Réordonner
            segment_stats = segment_stats.reindex(segment_order)
            
            # Ajouter des pourcentages
            total_clients = len(rfm)
            total_purchases = rfm['frequency'].sum()
            
            segment_stats['%_Clients'] = (segment_stats['Nb_Clients'] / total_clients * 100).round(1)
            segment_stats['%_Achats'] = (segment_stats['Total_Achats'] / total_purchases * 100).round(1)
            segment_stats['Achats_par_Client'] = (segment_stats['Total_Achats'] / segment_stats['Nb_Clients']).round(1)
            
            st.dataframe(segment_stats)
            
            # F. TOP CLIENTS
            st.subheader("🏆 Top 20 Clients par Fréquence d'Achat")
            
            top_clients = rfm.sort_values('frequency', ascending=False).head(20)
            top_clients['Rank'] = range(1, len(top_clients) + 1)
            
            fig = px.bar(top_clients.head(10), x='frequency', y='visitorid',
                        orientation='h',
                        title="Top 10 Clients les Plus Actifs",
                        hover_data=['Segment'],
                        labels={'frequency': 'Nombre d\'achats', 'visitorid': 'ID Client'},
                        color='frequency',
                        color_continuous_scale='thermal')
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Tableau complet
            st.dataframe(top_clients[['Rank', 'visitorid', 'frequency', 'Segment']].reset_index(drop=True))
            
            # G. ANALYSE DE LA VALEUR
            st.subheader("💰 Analyse de la Valeur Client")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Pareto analysis (80/20)
                sorted_clients = rfm.sort_values('frequency', ascending=False)
                sorted_clients['cumulative_pct'] = (sorted_clients['frequency'].cumsum() / 
                                                  sorted_clients['frequency'].sum() * 100)
                
                top_20_pct_clients = len(sorted_clients[sorted_clients['cumulative_pct'] <= 80])
                paretto_pct = (top_20_pct_clients / len(sorted_clients)) * 100
                
                st.metric("Règle 80/20", f"{paretto_pct:.1f}%", 
                         delta="% des clients font 80% des achats")
            
            with col2:
                # Churn potentiel
                one_time_buyers = len(rfm[rfm['frequency'] == 1])
                one_time_pct = (one_time_buyers / len(rfm)) * 100
                st.metric("Achats uniques", f"{one_time_pct:.1f}%",
                         delta=f"{one_time_buyers:,} clients")
            
            with col3:
                # Loyalty index
                repeat_buyers = len(rfm[rfm['frequency'] > 1])
                repeat_pct = (repeat_buyers / len(rfm)) * 100
                st.metric("Clients récurrents", f"{repeat_pct:.1f}%",
                         delta=f"{repeat_buyers:,} clients")
            
            # H. RECOMMANDATIONS STRATÉGIQUES
            st.subheader("🎯 Recommandations par Segment")
            
            recommendations = {
                'Clients VIP': """
                **Segment**: Top 10% des clients (≥ 90e percentile)
                **Caractéristiques**: Fréquence d'achat très élevée
                **Actions**:
                - Programme VIP exclusif
                - Service client prioritaire
                - Early access aux nouveautés
                - Invitations événements
                **Objectif**: Fidélisation maximale, ambassadeurs
                """,
                'Acheteurs très fréquents': """
                **Segment**: 75-90e percentile
                **Caractéristiques**: Fréquence élevée
                **Actions**:
                - Programme de fidélité
                - Offres personnalisées
                - Recommandations sur mesure
                **Objectif**: Conversion en Clients VIP
                """,
                'Acheteurs fréquents': """
                **Segment**: 50-75e percentile
                **Caractéristiques**: Fréquence moyenne-haute
                **Actions**:
                - Email marketing ciblé
                - Offres de cross-selling
                - Programme de parrainage
                **Objectif**: Augmenter la fréquence d'achat
                """,
                'Acheteurs réguliers': """
                **Segment**: 25-50e percentile (médiane)
                **Caractéristiques**: Fréquence moyenne
                **Actions**:
                - Campagnes de rappel
                - Offres de réactivation
                - Contenu éducatif
                **Objectif**: Maintenir et développer
                """,
                'Acheteurs occasionnels': """
                **Segment**: ≤ 25e percentile
                **Caractéristiques**: Faible fréquence (souvent 1 achat)
                **Actions**:
                - Email de bienvenue/suivi
                - Enquête de satisfaction
                - Offre de premier ré-achat
                **Objectif**: Conversion en clients récurrents
                """
            }
            
            selected_segment = st.selectbox(
                "Voir les recommandations pour:",
                list(recommendations.keys())
            )
            
            with st.expander(f"📋 Recommandations détaillées - {selected_segment}", expanded=True):
                st.markdown(recommendations[selected_segment])
            
            # I. EXPORT DES DONNÉES
            st.subheader("💾 Export des données")
            
            if st.button("📥 Télécharger les segments RFM"):
                csv = rfm.to_csv(index=False)
                st.download_button(
                    label="Télécharger CSV",
                    data=csv,
                    file_name="segments_rfm.csv",
                    mime="text/csv"
                )
        
        else:
            st.warning("⚠️ Aucune transaction trouvée pour l'analyse RFM")
            
# 7. ABANDONS PANIER
elif option == "Abandons panier":
    st.header("🛍️ Analyse des Abandons de Panier")
    
    if 'event' in events.columns and 'itemid' in events.columns:
        # Métriques d'abandon
        produits_panier = events[events['event'] == 'addtocart']['itemid'].unique()
        produits_achetes = events[events['event'] == 'transaction']['itemid'].unique()
        
        # Convertir en sets pour les opérations
        produits_panier_set = set(produits_panier)
        produits_achetes_set = set(produits_achetes)
        produits_abandonnes = list(produits_panier_set - produits_achetes_set)
        
        # Calculer le taux d'abandon
        taux_abandon = (len(produits_abandonnes) / len(produits_panier) * 100) if len(produits_panier) > 0 else 0
        
        # Afficher les métriques principales
        st.subheader("📊 Métriques d'Abandon")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Produits panier",
                f"{len(produits_panier):,}",
                delta="Ajoutés"
            )
        
        with col2:
            st.metric(
                "Produits achetés",
                f"{len(produits_achetes):,}",
                delta="Transactions"
            )
        
        with col3:
            st.metric(
                "Produits abandonnés",
                f"{len(produits_abandonnes):,}",
                delta="Non convertis"
            )
        
        with col4:
            st.metric(
                "Taux d'abandon",
                f"{taux_abandon:.1f}%",
                delta="Produits panier → achat"
            )
        
        # TOP 10 PRODUITS LES PLUS ABANDONNÉS
        st.subheader("🔥 Top 10 Produits les Plus Abandonnés")
        
        # Calculer les abandons par produit
        abandons_par_produit = events[
            (events['event'] == 'addtocart') & 
            (~events['itemid'].isin(produits_achetes))
        ]['itemid'].value_counts().head(10)
        
        if not abandons_par_produit.empty:
            # Préparer les données pour le graphique
            top_abandons_df = abandons_par_produit.reset_index()
            top_abandons_df.columns = ['itemid', 'abandons']
            
            # Calculer le taux d'abandon pour chaque produit
            taux_abandons = []
            for produit in top_abandons_df['itemid']:
                total_ajouts = events[
                    (events['itemid'] == produit) & 
                    (events['event'] == 'addtocart')
                ].shape[0]
                taux = (top_abandons_df.loc[top_abandons_df['itemid'] == produit, 'abandons'].iloc[0] / total_ajouts * 100) if total_ajouts > 0 else 0
                taux_abandons.append(taux)
            
            top_abandons_df['taux_abandon'] = taux_abandons
            top_abandons_df['taux_abandon'] = top_abandons_df['taux_abandon'].round(1)
            
            # Créer le graphique des top abandons
            fig = go.Figure()
            
            # Ajouter les barres pour le nombre d'abandons
            fig.add_trace(go.Bar(
                y=[f'Produit {pid}' for pid in top_abandons_df['itemid']],
                x=top_abandons_df['abandons'],
                orientation='h',
                name='Nombre d\'abandons',
                marker_color='red',
                opacity=0.7,
                text=top_abandons_df['abandons'].astype(str) + ' abandons',
                textposition='outside',
                textfont=dict(size=10, weight='bold')
            ))
            
            # Ajouter une annotation pour le taux d'abandon
            for i, (abandons, taux) in enumerate(zip(top_abandons_df['abandons'], top_abandons_df['taux_abandon'])):
                fig.add_annotation(
                    x=abandons / 2,  # Position au milieu de la barre
                    y=i,
                    text=f"{taux}%",
                    showarrow=False,
                    font=dict(color='white', size=11, weight='bold'),
                    bgcolor='rgba(0,0,0,0.5)',
                    bordercolor='white',
                    borderwidth=1,
                    borderpad=3
                )
            
            fig.update_layout(
                title='TOP 10 PRODUITS LES PLUS ABANDONNÉS',
                title_font=dict(size=16, weight='bold'),
                xaxis_title='Nombre d\'Abandons',
                yaxis_title='Produit',
                plot_bgcolor='white',
                height=500,
                yaxis=dict(autorange='reversed'),
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # TABLEAU DÉTAILLÉ DES TOP ABANDONS
            with st.expander("📋 Voir le tableau détaillé des abandons"):
                # Ajouter plus d'informations au dataframe
                top_abandons_df['rank'] = range(1, len(top_abandons_df) + 1)
                top_abandons_df['total_ajouts'] = [
                    events[(events['itemid'] == pid) & (events['event'] == 'addtocart')].shape[0]
                    for pid in top_abandons_df['itemid']
                ]
                
                # Calculer les taux de conversion
                top_abandons_df['conversions'] = [
                    events[(events['itemid'] == pid) & (events['event'] == 'transaction')].shape[0]
                    for pid in top_abandons_df['itemid']
                ]
                
                top_abandons_df['taux_conversion'] = (top_abandons_df['conversions'] / top_abandons_df['total_ajouts'] * 100).round(1)
                
                # Afficher le tableau
                display_df = top_abandons_df[['rank', 'itemid', 'abandons', 'total_ajouts', 
                                            'taux_abandon', 'conversions', 'taux_conversion']]
                display_df.columns = ['Rang', 'ID Produit', 'Abandons', 'Total Ajouts Panier', 
                                    'Taux Abandon %', 'Conversions', 'Taux Conversion %']
                
                st.dataframe(display_df, use_container_width=True)
                
                # Télécharger les données
                csv = display_df.to_csv(index=False)
                st.download_button(
                    label="📥 Télécharger les données d'abandon",
                    data=csv,
                    file_name="top_abandons_panier.csv",
                    mime="text/csv"
                )
            
            # ANALYSE DES CAUSES POTENTIELLES
            st.subheader("🔍 Analyse des Causes d'Abandon")
            
            # Calculer les statistiques moyennes
            if len(top_abandons_df) > 0:
                avg_abandon_rate = top_abandons_df['taux_abandon'].mean()
                max_abandon_rate = top_abandons_df['taux_abandon'].max()
                min_abandon_rate = top_abandons_df['taux_abandon'].min()
                
                col_anal1, col_anal2, col_anal3 = st.columns(3)
                
                with col_anal1:
                    st.metric(
                        "Taux abandon moyen",
                        f"{avg_abandon_rate:.1f}%",
                        delta="Sur les top 10"
                    )
                
                with col_anal2:
                    st.metric(
                        "Pire taux abandon",
                        f"{max_abandon_rate:.1f}%",
                        delta="Produit critique"
                    )
                
                with col_anal3:
                    st.metric(
                        "Meilleur taux abandon",
                        f"{min_abandon_rate:.1f}%",
                        delta="Plus performant"
                    )
                
                # Recommandations spécifiques
                st.info(f"""
                **Insights sur les abandons:**
                
                - **{top_abandons_df.iloc[0]['itemid']}** est le produit le plus abandonné ({top_abandons_df.iloc[0]['abandons']:,} abandons)
                - Taux d'abandon moyen des top 10: **{avg_abandon_rate:.1f}%**
                - Le produit avec le pire taux: **{top_abandons_df.loc[top_abandons_df['taux_abandon'].idxmax(), 'itemid']}** ({max_abandon_rate:.1f}%)
                """)
            
            # FUNNEL D'ABANDON
            st.subheader("📉 Funnel d'Abandon")
            
            # Calculer les étapes du funnel
            produits_vus = events[events['event'] == 'view']['itemid'].nunique()
            produits_panier_count = len(produits_panier)
            produits_achetes_count = len(produits_achetes)
            
            funnel_data = pd.DataFrame({
                'Étape': ['Produits Vus', 'Ajoutés au Panier', 'Achetés'],
                'Nombre': [produits_vus, produits_panier_count, produits_achetes_count],
                'Taux Conversion': [100, 
                                  (produits_panier_count/produits_vus*100) if produits_vus>0 else 0,
                                  (produits_achetes_count/produits_panier_count*100) if produits_panier_count>0 else 0]
            })
            
            # Créer le funnel graphique
            fig_funnel = go.Figure(go.Funnel(
                y=funnel_data['Étape'],
                x=funnel_data['Nombre'],
                textinfo="value+percent initial",
                opacity=0.65,
                marker=dict(
                    color=['lightblue', 'orange', 'green'],
                    line=dict(width=2, color='white')
                )
            ))
            
            fig_funnel.update_layout(
                title='FUNNEL DE CONVERSION AVEC ABANDONS',
                title_font=dict(size=14, weight='bold'),
                showlegend=False
            )
            
            st.plotly_chart(fig_funnel, use_container_width=True)
            
            # Afficher les taux de conversion
            col_f1, col_f2 = st.columns(2)
            
            with col_f1:
                taux_vue_panier = (produits_panier_count / produits_vus * 100) if produits_vus > 0 else 0
                st.metric(
                    "Vue → Panier",
                    f"{taux_vue_panier:.1f}%",
                    delta=f"{produits_panier_count:,}/{produits_vus:,}"
                )
            
            with col_f2:
                taux_panier_achat = (produits_achetes_count / produits_panier_count * 100) if produits_panier_count > 0 else 0
                st.metric(
                    "Panier → Achat",
                    f"{taux_panier_achat:.1f}%",
                    delta=f"{produits_achetes_count:,}/{produits_panier_count:,}"
                )
            
            
            # TOP PRODUITS À SURVEILLER
            with st.expander("⚠️ Produits à surveiller (risque élevé d'abandon)"):
                # Produits avec taux d'abandon > 50%
                produits_risque = top_abandons_df[top_abandons_df['taux_abandon'] > 50]
                
                if not produits_risque.empty:
                    for _, row in produits_risque.iterrows():
                        st.warning(
                            f"**Produit {row['itemid']}** - "
                            f"{row['taux_abandon']}% d'abandon "
                            f"({row['abandons']} abandons sur {row['total_ajouts']} ajouts)"
                        )
                else:
                    st.info("Aucun produit avec un taux d'abandon critique (>50%)")
        
        else:
            st.info("Aucun abandon de panier détecté dans les données")
    
    else:
        st.warning("⚠️ Les colonnes nécessaires ('event', 'itemid') ne sont pas disponibles")

# Footer
st.markdown("---")
st.caption("Dashboard E-commerce - Analyse des données utilisateur")