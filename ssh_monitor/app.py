import streamlit as st
import pandas as pd

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(
    page_title="MonitorSSH",
    page_icon="🔒",
    layout="wide"
)

# 2. CHARGEMENT ET PRÉPARATION (ETL)
@st.cache_data
def load_data():
    # Chargement
    df = pd.read_csv('datasetssh.csv')
    
    # CONVERSION CRUCIALE : Transformer le texte en dates
    # 'coerce' permet de gérer les erreurs si une date est mal formée
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
    
    return df

# 3. INTERFACE PRINCIPALE
def main():
    st.title("🔒 MonitorSSH - Dashboard de Sécurité")
    
    # Chargement des données
    try:
        df_brut = load_data()
    except FileNotFoundError:
        st.error("Fichier datasetssh.csv introuvable.")
        return

    # --- SIDEBAR (Barre latérale) ---
    st.sidebar.header("Filtres")
    
    # Filtre 1 : Date
    # On récupère les dates min et max du fichier pour configurer le filtre
    min_date = df_brut['Timestamp'].min()
    max_date = df_brut['Timestamp'].max()
    
    start_date = st.sidebar.date_input(
        "Date de début", 
        min_date,
        min_value=min_date,
        max_value=max_date
    )
    
    end_date = st.sidebar.date_input(
        "Date de fin", 
        max_date,
        min_value=min_date,
        max_value=max_date
    )

    # Filtre 2 : Event ID (Multiselection)
    # On liste tous les EventId uniques
    all_event_ids = df_brut['EventId'].unique()
    selected_events = st.sidebar.multiselect(
        "Sélectionner les EventId",
        all_event_ids,
        default=all_event_ids # Par défaut, tout est sélectionné
    )

    # --- APPLICATION DES FILTRES ---
    # On crée une copie filtrée (masque booléen)
    # 1. Filtrer par date (on convertit l'input date en datetime pour comparer)
    mask_date = (df_brut['Timestamp'].dt.date >= start_date) & (df_brut['Timestamp'].dt.date <= end_date)
    # 2. Filtrer par EventId
    mask_event = df_brut['EventId'].isin(selected_events)
    
    # On combine les deux filtres
    df_filtered = df_brut[mask_date & mask_event]

    # --- AFFICHAGE DES RÉSULTATS ---
    st.markdown("---")
    
    # KPIs (Indicateurs Clés) mis à jour dynamiquement
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Logs (Filtrés)", df_filtered.shape[0])
    with col2:
        # Calcul du pourcentage conservé
        pourcentage = (len(df_filtered) / len(df_brut)) * 100
        st.metric("% du Dataset", f"{pourcentage:.1f}%")
    with col3:
        # Compte des IPs uniques dans la sélection
        st.metric("IPs Uniques", df_filtered['SourceIP'].nunique())

    # Tableau
    st.subheader("📋 Logs Filtrés")
    st.dataframe(df_filtered, use_container_width=True)


    st.markdown("---")
    st.header("📊 Analyse Visuelle")

    # Création de deux colonnes pour les graphiques
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("Top 10 IPs Attaquantes")
        # Calcul du Top 10
        top_ips = df_filtered['SourceIP'].value_counts().head(10)
        # Affichage simple avec Streamlit
        st.bar_chart(top_ips)

    with chart_col2:
        st.subheader("Volume d'attaques par Heure")
        # On groupe par heure pour voir les pics
        # On utilise set_index pour que Streamlit comprenne que c'est une série temporelle
        if not df_filtered.empty:
            time_series = df_filtered.set_index('Timestamp').resample('H').size()
            st.line_chart(time_series)
        else:
            st.info("Aucune donnée pour cette période.")

    # Section Analyse Avancée (Bonus)
    st.markdown("---")
    st.subheader("🚨 Top Usernames Tentés")
    # On exclut les valeurs 'None' ou vides si besoin
    top_users = df_filtered['User'].value_counts().head(10)
    st.bar_chart(top_users)


if __name__ == "__main__":
    main()
