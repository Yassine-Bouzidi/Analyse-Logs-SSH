import streamlit as st
import pandas as pd
import requests
import os
import time  # Pour gérer les pauses API
import altair as alt  # Pour les graphiques avancés

script_dir = os.path.dirname(__file__)

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(
    page_title="MonitorSSH",
    page_icon="🔒",
    layout="wide"
)

# 2. CHARGEMENT ET PRÉPARATION (ETL)
@st.cache_data
def load_data(file_path_or_buffer):
    """Charge les données depuis un chemin de fichier OU un fichier uploadé."""
    df = pd.read_csv(file_path_or_buffer)
    if 'Timestamp' in df.columns:
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
    else:
        st.error("Erreur: Le fichier CSV doit contenir une colonne 'Timestamp'.")
        return pd.DataFrame()
    return df

@st.cache_data
def get_locations(ip_list):
    """Récupère lat/lon pour une liste d'IPs uniques via ip-api.com (batch)."""
    locations = []
    unique_ips = list(set(ip_list))
    
    # L'API batch supporte max 100 IPs par appel
    # Pour afficher TOUT sans se faire bannir, on doit ralentir la boucle
    for i in range(0, len(unique_ips), 100):
        batch = unique_ips[i:i+100]
        try:
            response = requests.post(
                "http://ip-api.com/batch", 
                json=[{"query": ip, "fields": "lat,lon,country,query"} for ip in batch]
            ).json()
            
            for item in response:
                if 'lat' in item and 'lon' in item:
                    locations.append({
                        'ip': item['query'], 
                        'lat': item['lat'], 
                        'lon': item['lon'],
                        'country': item.get('country', 'Inconnu')
                    })
            
            # --- PAUSE DE SÉCURITÉ ---
            # L'API gratuite limite à 45 requêtes/minute.
            # On fait une pause de 1.5s entre chaque lot de 100 IPs pour être sûr de passer.
            time.sleep(1.5) 
            
        except Exception as e:
            st.error(f"Erreur de géolocalisation : {e}")
            break
            
    return pd.DataFrame(locations)


# 3. INTERFACE PRINCIPALE
def main():
    st.title("🔒 Dashboard de Sécurité : Clinique Tamalou")
    
    # --- UPLOAD DE FICHIER ---
    st.sidebar.header("📁 Données")
    uploaded_file = st.sidebar.file_uploader("Charger un nouveau fichier CSV", type=['csv'])

    if uploaded_file is not None:
        st.sidebar.success("Fichier personnalisé chargé !")
        df_brut = load_data(uploaded_file)
    else:
        try:
            csv_path = os.path.join(script_dir, 'datasetssh.csv')
            df_brut = load_data(csv_path)
            st.sidebar.info("Utilisation du fichier de démo par défaut.")
        except FileNotFoundError:
            st.error(f"Fichier de démo 'datasetssh.csv' introuvable.")
            return

    if df_brut.empty:
        return

    # --- SIDEBAR FILTRES ---
    st.sidebar.header("Filtres")
    
    min_date = df_brut['Timestamp'].min()
    max_date = df_brut['Timestamp'].max()
    
    start_date = st.sidebar.date_input("Date de début", min_date, min_value=min_date, max_value=max_date)
    end_date = st.sidebar.date_input("Date de fin", max_date, min_value=min_date, max_value=max_date)

    all_event_ids = df_brut['EventId'].unique()
    selected_events = st.sidebar.multiselect("Sélectionner les EventId", all_event_ids, default=all_event_ids)

    all_ips = df_brut['SourceIP'].unique()
    selected_ip = st.sidebar.selectbox("Rechercher une IP spécifique", options=["Toutes"] + list(all_ips))

    # --- APPLICATION DES FILTRES ---
    mask_date = (df_brut['Timestamp'].dt.date >= start_date) & (df_brut['Timestamp'].dt.date <= end_date)
    mask_event = df_brut['EventId'].isin(selected_events)
    df_filtered = df_brut[mask_date & mask_event]

    if selected_ip != "Toutes":
        df_filtered = df_filtered[df_filtered['SourceIP'] == selected_ip]

    # --- AFFICHAGE DES RÉSULTATS ---
    st.markdown("---")
    
    if df_filtered.empty:
        st.warning("⚠️ Aucune donnée ne correspond à vos filtres.")
    else:
        # KPIs
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Total Logs (Filtrés)", df_filtered.shape[0])
        with col2: st.metric("% du Dataset", f"{(len(df_filtered) / len(df_brut)) * 100:.1f}%")
        with col3: st.metric("IPs Uniques", df_filtered['SourceIP'].nunique())

        # Tableau
        st.subheader("📋 Logs Filtrés")
        st.dataframe(df_filtered, use_container_width=True)

        st.markdown("---")
        st.header("📊 Analyse Visuelle")

        # Graphiques
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.subheader("Top 10 IPs Attaquantes")
            st.bar_chart(df_filtered['SourceIP'].value_counts().head(10))

        with chart_col2:
            st.subheader("Volume d'attaques par Heure")
            st.line_chart(df_filtered.set_index('Timestamp').resample('H').size())

        st.markdown("---")
        st.subheader("🚨 Top Usernames Tentés")
        st.bar_chart(df_filtered['User'].value_counts().head(10))

        # --- CARTE GÉOGRAPHIQUE ---
        st.markdown("---")
        st.header("🌍 Carte des Attaques")

        if 'SourceIP' in df_filtered.columns:
            ips_to_locate = df_filtered['SourceIP'].dropna().unique().tolist()
            
            if len(ips_to_locate) > 0:
                st.info(f"Géolocalisation de {len(ips_to_locate)} adresses IP uniques en cours... Cela peut prendre un moment.")
                
                with st.spinner("Interrogation de l'API de localisation..."):
                    df_locations = get_locations(ips_to_locate)

                if not df_locations.empty:
                    # 1. La Carte
                    st.map(df_locations, size=20, color='#FF0000')
                    st.caption(f"{len(df_locations)} localisations trouvées.")
                    
                    # 2. Le Graphique Top Pays (Corrigé avec Altair pour le tri)
                    st.subheader("📊 Top 10 des Pays d'origine")
                    
                    # Préparation des données pour Altair
                    top_countries = df_locations['country'].value_counts().head(10).reset_index()
                    top_countries.columns = ['Pays', 'Nombre']
                    
                    # Création du graphique Altair trié
                    chart = alt.Chart(top_countries).mark_bar().encode(
                        x=alt.X('Pays', sort='-y', title='Pays'), # Tri décroissant sur Y
                        y=alt.Y('Nombre', title="Nombre d'attaques"),
                        tooltip=['Pays', 'Nombre']
                    ).properties(
                        height=400
                    )
                    
                    st.altair_chart(chart, use_container_width=True)

                else:
                    st.warning("Aucune localisation trouvée.")
            else:
                 st.info("Aucune IP à localiser avec les filtres actuels.")
        else:
            st.error("Colonne 'SourceIP' introuvable.")

if __name__ == "__main__":
    main()
