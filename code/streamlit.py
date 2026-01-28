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
    
    if 'timestamp' in events.columns:
        # Extraire composantes temporelles
        events['heure'] = events['timestamp'].dt.hour
        events['jour_semaine'] = events['timestamp'].dt.day_name()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Par heure
            hourly = events.groupby('heure').size().reset_index(name='count')
            fig = px.line(hourly, x='heure', y='count', title="Activité par heure")
            st.plotly_chart(fig, use_container_width=True)
            
            # Heure de pointe
            peak_hour = hourly.loc[hourly['count'].idxmax(), 'heure']
            st.info(f"**Heure de pointe**: {peak_hour}:00")
        
        with col2:
            # Par jour de semaine
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            daily = events.groupby('jour_semaine').size().reindex(day_order).reset_index(name='count')
            fig = px.bar(daily, x='jour_semaine', y='count', title="Activité par jour de semaine")
            st.plotly_chart(fig, use_container_width=True)
            
            # Jour le plus actif
            peak_day = daily.loc[daily['count'].idxmax(), 'jour_semaine']
            st.info(f"**Jour le plus actif**: {peak_day}")

# 5. COMPORTEMENT UTILISATEUR
elif option == "Comportement utilisateur":
    st.header("👤 Comportement utilisateur")
    
    if 'visitorid' in events.columns:
        # Distribution des sessions
        sessions_per_user = events.groupby('visitorid').size().reset_index(name='sessions')
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.histogram(sessions_per_user, x='sessions', nbins=50, 
                              title="Distribution des sessions par utilisateur")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Taux de conversion par utilisateur
            if 'event' in events.columns:
                user_conversion = events.groupby('visitorid')['event'].apply(
                    lambda x: (x == 'transaction').any()
                ).reset_index(name='a_achete')
                
                conversion_rate = user_conversion['a_achete'].mean() * 100
                
                fig = px.pie(user_conversion, names='a_achete', 
                            title=f"Utilisateurs avec achat ({conversion_rate:.1f}%)")
                st.plotly_chart(fig, use_container_width=True)
        
        # Top utilisateurs
        st.subheader("Top 10 utilisateurs les plus actifs")
        top_users = sessions_per_user.sort_values('sessions', ascending=False).head(10)
        fig = px.bar(top_users, x='sessions', y='visitorid', orientation='h')
        st.plotly_chart(fig, use_container_width=True)

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
    st.header("🛍️ Abandons de panier")
    
    if 'event' in events.columns:
        add_to_cart = events[events['event'] == 'addtocart']
        transactions = events[events['event'] == 'transaction']
        
        if len(add_to_cart) > 0:
            # Métriques
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Ajouts panier", f"{len(add_to_cart):,}")
            
            with col2:
                st.metric("Transactions", f"{len(transactions):,}")
            
            with col3:
                abandon_rate = (1 - len(transactions)/len(add_to_cart)) * 100 if len(add_to_cart) > 0 else 0
                st.metric("Taux d'abandon", f"{abandon_rate:.1f}%")
            
            # Top produits abandonnés
            if 'itemid' in events.columns:
                cart_items = add_to_cart.groupby('itemid').size().reset_index(name='ajouts')
                bought_items = transactions.groupby('itemid').size().reset_index(name='achats')
                
                abandonment = cart_items.merge(bought_items, on='itemid', how='left')
                abandonment['achats'] = abandonment['achats'].fillna(0)
                abandonment['abandons'] = abandonment['ajouts'] - abandonment['achats']
                abandonment = abandonment.sort_values('abandons', ascending=False).head(20)
                
                st.subheader("Top 10 produits les plus abandonnés")
                fig = px.bar(abandonment.head(10), x='abandons', y='itemid', orientation='h')
                st.plotly_chart(fig, use_container_width=True)
                
                st.dataframe(abandonment)
        
        else:
            st.warning("Aucun ajout au panier trouvé")

# Footer
st.markdown("---")
st.caption("Dashboard E-commerce - Analyse des données utilisateur")