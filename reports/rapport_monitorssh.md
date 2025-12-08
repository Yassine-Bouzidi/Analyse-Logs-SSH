# RAPPORT TECHNIQUE COMPLET : MONITORSSH
## Dashboard de Sécurité - Analyse de Logs SSH

---

**Projet :** MonitorSSH - Web App de Monitoring SSH  
**Auteur :** Yassine Bouzidi  
**Date :** 8 Décembre 2025  
**Formation :** Simplon - Cybersécurité  
**Technologie :** Python, Streamlit, Pandas, GitHub, Streamlit Cloud  
**Lien Public :** https://dashboard-ssh-ysn.streamlit.app  
**Dépôt GitHub :** https://github.com/Yassine-Bouzidi/Analyse-Logs-SSH

---

## TABLE DES MATIÈRES
1. Contexte et Objectifs
2. Architecture Technique
3. Étapes de Développement (Jour 1 & Jour 2)
4. Code Détaillé avec Explications
5. Déploiement et Production
6. Résultats et Métriques
7. Améliorations Futures

---

## 1. CONTEXTE ET OBJECTIFS

### Problématique
Les administrateurs système et les responsables sécurité (CISO) reçoivent quotidiennement des centaines de milliers de logs SSH bruts. Ces données sont :
- **Non structurées** : texte brut, difficile à parcourir
- **Énormes** : 655 147 entrées dans notre cas
- **Inutilisables** : sans outils de visualisation adéquats

### Solution Apportée
Développer une **Web App interactive** (SaaS) permettant de :
1. Charger des fichiers de logs SSH en format CSV
2. Filtrer les données par plusieurs critères (dates, types d'événements, adresses IP)
3. Visualiser les données sous forme de graphiques et tableaux
4. Identifier rapidement les menaces et les patterns d'attaque
5. Déployer publiquement pour accès multi-utilisateurs

### Résultat
Une application professionnelle, stable, hébergée gratuitement sur Streamlit Cloud et accessible depuis n'importe quel navigateur web.

---

## 2. ARCHITECTURE TECHNIQUE

### 2.1 Stack Technologique

```
┌─────────────────────────────────────────────────────────┐
│                 FRONTEND (Navigateur)                    │
│        - Streamlit UI (Sidebar, Graphiques, Tableaux)   │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/HTTPS
┌────────────────────▼────────────────────────────────────┐
│           BACKEND (Streamlit Server)                     │
│  - Python 3.10+                                          │
│  - Pandas (Traitement de données)                        │
│  - Cache (@st.cache_data)                               │
└────────────────────┬────────────────────────────────────┘
                     │ Lecture de fichiers
┌────────────────────▼────────────────────────────────────┐
│              STOCKAGE (GitHub + Cloud)                   │
│  - app.py, requirements.txt (GitHub)                     │
│  - datasetssh.csv (Dépôt GitHub)                         │
│  - Déploiement via Streamlit Cloud                       │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Fonctionnement du Cache (@st.cache_data)

**Le cache est crucial pour la performance.**

Sans cache :
- À chaque clic sur un filtre → Rechargement du CSV (655k lignes)
- **Temps d'attente :** 2-3 secondes par interaction
- **Expérience utilisateur :** Frustrante

Avec cache (@st.cache_data) :
- Premier chargement : Sauvegarde le DataFrame en mémoire
- Interactions suivantes : Lecture depuis la RAM (instantané)
- **Temps d'attente :** <100ms
- **Expérience utilisateur :** Fluide et responsive

---

## 3. ÉTAPES DE DÉVELOPPEMENT

### JOUR 1 : Architecture et Premiers Affichages

#### Étape 1 : Préparation du Projet
```
ssh_monitor/
├── app.py                 # Fichier principal Streamlit
├── requirements.txt       # Dépendances Python
├── .gitignore            # Fichiers à ignorer lors du push GitHub
└── datasetssh.csv        # Données de démo
```

**Fichiers créés :**

**1. requirements.txt**
```
streamlit
pandas
matplotlib
```
Contient les librairies nécessaires. À installer avec : `pip install -r requirements.txt`

**2. .gitignore**
```
.venv/
__pycache__/
*.pyc
.DS_Store
```
Indique à Git quels fichiers IGNORER lors du commit (évite de versionner l'environnement virtuel lourd).

#### Étape 2 : Code Initial (app.py)
**Voir section 4 pour explications ligne par ligne.**

#### Étape 3 : Lancement Local
```bash
streamlit run app.py
```
L'app s'ouvre automatiquement sur `localhost:8501`.

---

### JOUR 2 : Interactivité et Production

#### Phase 1 : Ajout des Filtres (Sidebar)
- Filtre par plage de dates
- Filtre par type d'événement (multiselect)
- Filtre par IP spécifique

#### Phase 2 : Visualisation (Graphiques)
- Bar Chart : Top 10 IPs attaquantes
- Line Chart : Volume d'attaques par heure
- Bar Chart : Usernames les plus tentés

#### Phase 3 : Déploiement (GitHub + Streamlit Cloud)
1. Initialiser Git : `git init`
2. Commit initial : `git commit -m "Initial commit"`
3. Push GitHub : `git push`
4. Déployer sur Streamlit Cloud (lien du repo)
5. App publique en ligne (URL `dashboard-ssh-ysn.streamlit.app`)

#### Phase 4 : Bonus (Upload de fichier)
Ajout de la fonctionnalité `st.file_uploader` pour permettre aux utilisateurs de charger leurs propres fichiers CSV.

---

## 4. CODE DÉTAILLÉ AVEC EXPLICATIONS

### 4.1 Configuration et Imports

```python
# ======== LIGNE 1 : IMPORT STREAMLIT ========
import streamlit as st
# Streamlit est le framework qui crée l'interface web.
# Il gère automatiquement la conversion de code Python en UI interactive.
# Alternative : Flask/Django (plus lourd)

# ======== LIGNE 2 : IMPORT PANDAS ========
import pandas as pd
# Pandas est la librairie standard pour manipuler les données (DataFrames).
# Un DataFrame est comme une table Excel : lignes + colonnes
```

### 4.2 Configuration de la Page Streamlit

```python
# ======== CONFIGURATION DE PAGE ========
st.set_page_config(
    # POINT CRUCIAL : Cette fonction DOIT être appelée avant tout autre code Streamlit !
    page_title="MonitorSSH",
    # Définit le titre qui apparaît dans l'onglet du navigateur
    # Exemple dans la barre du navigateur : [MonitorSSH] ← C'est ça
    
    page_icon="🔒",
    # Définit l'emoji qui apparaît dans l'onglet du navigateur (c'est cosmétique mais professionnel)
    
    layout="wide"
    # "wide" = utilise toute la largeur de l'écran (mieux pour les graphiques larges)
    # Alternative : "centered" = contenu centré (moins de place)
)
```

### 4.3 Fonction de Chargement (ETL)

```python
# ======== DÉCORATEUR CACHE - TRÈS IMPORTANT ========
@st.cache_data
# Ce décorateur dit à Streamlit : "Sauvegarde le résultat de cette fonction en mémoire"
# Si on l'appelle avec les mêmes paramètres, retourne la version en cache (pas de rechargement)

def load_data(file_path_or_buffer):
    # Paramètre "file_path_or_buffer" = flexibilité totale
    # Peut être soit :
    #   - Un string : 'datasetssh.csv' (chemin local)
    #   - Un objet fichier : uploaded_file (fichier uploadé par l'utilisateur)
    
    # ======== LIGNE 1 : CHARGEMENT CSV ========
    df = pd.read_csv(file_path_or_buffer)
    # pd.read_csv() lit un fichier CSV et le convertit en DataFrame
    # DataFrame = structure de données 2D (comme une table SQL)
    # Exemple :
    # | Timestamp        | EventId | SourceIP | User | Raw_Message |
    # |------------------|---------|----------|------|-------------|
    # | 2024-12-10...    | E27     | 173.2... | None | reverse ... |
    
    # ======== LIGNE 2 : VÉRIFICATION COLONNE ========
    if 'Timestamp' in df.columns:
        # Vérifier que la colonne 'Timestamp' existe
        # Si elle n'existe pas, on ne peut pas faire l'analyse temporelle
        
        # ======== LIGNE 3 : CONVERSION DE DATES ========
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        # Convertit la colonne texte '2024-12-10 06:55:46' en objet datetime
        # errors='coerce' = si une date est mal formée, la remplacer par NaT (Not a Time)
        # Pourquoi important ? Permet les comparaisons : date1 > date2 (sinon erreur)
        
    else:
        # Si colonne Timestamp n'existe pas
        st.error("Erreur: Le fichier CSV doit contenir une colonne 'Timestamp'.")
        # Affiche un message d'erreur en rouge dans l'interface
        return pd.DataFrame()
        # Retourne un DataFrame vide (signale une erreur)
    
    # ======== LIGNE 4 : RETOUR ========
    return df
    # Retourne le DataFrame nettoyé et prêt à l'emploi
```

### 4.4 Fonction Principale (Interface)

```python
# ======== DÉFINITION DE LA FONCTION PRINCIPALE ========
def main():
    # Toute la logique de l'interface est encapsulée dans cette fonction
    # C'est un pattern propre en Python
    
    # ======== TITRE ========
    st.title("🔒 Dashboard de Sécurité : Clinique Tamalou")
    # Crée un titre de niveau 1 (équivalent à <h1> en HTML)
    # L'emoji 🔒 donne un aspect "sécurité"
    
    # ======== SIDEBAR - UPLOAD DE FICHIER ========
    st.sidebar.header("📁 Données")
    # "st.sidebar" = tout ce qui suit apparaît dans la barre latérale gauche
    # header() = titre de section
    
    uploaded_file = st.sidebar.file_uploader(
        "Charger un nouveau fichier CSV",
        # Label du bouton
        type=['csv']
        # Restriction : seuls les fichiers .csv sont acceptés
    )
    # file_uploader() retourne un objet fichier (ou None si rien n'est uploadé)
    
    # ======== LOGIQUE DE CHARGEMENT ========
    if uploaded_file is not None:
        # Si l'utilisateur A uploadé un fichier personnalisé
        st.sidebar.success("Fichier personnalisé chargé !")
        # Message de succès (en vert)
        df_brut = load_data(uploaded_file)
        # Charge le fichier uploadé
        
    else:
        # Si l'utilisateur N'a RIEN uploadé
        try:
            # "try" = essayer d'exécuter le code suivant
            # "except" = si une erreur surgit, faire quelque chose
            
            df_brut = load_data('datasetssh.csv')
            # Charge le fichier de démo par défaut
            st.sidebar.info("Utilisation du fichier de démo par défaut.")
            # Message informatif (en bleu)
            
        except FileNotFoundError:
            # Si 'datasetssh.csv' n'existe pas
            st.error("Fichier de démo 'datasetssh.csv' introuvable.")
            return
            # Arrête l'exécution (pas de données = pas d'interface)
    
    # ======== SÉCURITÉ : DATAFRAME VIDE ? ========
    if df_brut.empty:
        # Si le DataFrame est vide (pas une seule ligne)
        return
        # Arrête tout (erreur critique)
    
    # ======== SIDEBAR - FILTRES ========
    st.sidebar.header("Filtres")
    # Nouveau titre de section dans la sidebar
    
    # -------- FILTRE 1 : DATES --------
    # On récupère les dates min/max du dataset pour les bornes
    min_date = df_brut['Timestamp'].min()
    # min() retourne la date la plus ANCIENNE
    max_date = df_brut['Timestamp'].max()
    # max() retourne la date la plus RÉCENTE
    
    start_date = st.sidebar.date_input(
        "Date de début",
        # Label
        min_date,
        # Valeur par défaut (première date du dataset)
        min_value=min_date,
        # L'utilisateur ne peut pas aller AVANT cette date
        max_value=max_date
        # L'utilisateur ne peut pas aller APRÈS cette date
    )
    # Retourne un objet date (ex : datetime.date(2024, 12, 10))
    
    end_date = st.sidebar.date_input(
        "Date de fin",
        max_date,
        min_value=min_date,
        max_value=max_date
    )
    
    # -------- FILTRE 2 : EVENT ID (Type d'attaque) --------
    all_event_ids = df_brut['EventId'].unique()
    # unique() retourne les valeurs UNIQUES (sans doublon) de la colonne
    # Exemple : ['E27', 'E13', 'E12', 'E21', ...] (environ 10 types d'événements)
    
    selected_events = st.sidebar.multiselect(
        "Sélectionner les EventId",
        # Label
        all_event_ids,
        # Liste des options disponibles
        default=all_event_ids
        # Par défaut, TOUS les EventId sont sélectionnés
    )
    # Retourne une LISTE des valeurs cochées par l'utilisateur
    # Exemple : ['E27', 'E13', 'E12'] (l'utilisateur a décroché E21)
    
    # -------- FILTRE 3 : IP SPÉCIFIQUE --------
    all_ips = df_brut['SourceIP'].unique()
    # Liste de toutes les IPs du dataset (ex: ['173.234.31.186', '183.129.154.138', ...])
    
    selected_ip = st.sidebar.selectbox(
        "Rechercher une IP spécifique",
        # Label
        options=["Toutes"] + list(all_ips)
        # OPTIONS = ["Toutes", '173.234.31.186', '183.129.154.138', ...]
        # "Toutes" permet de ne PAS filtrer par IP
    )
    # Retourne UNE SEULE valeur sélectionnée par l'utilisateur (pas une liste)
    # Exemple : "173.234.31.186" ou "Toutes"
    
    # ======== APPLICATION DES FILTRES ========
    # Créer des "masques booléens" (True/False pour chaque ligne)
    
    # -------- MASQUE 1 : DATES --------
    mask_date = (df_brut['Timestamp'].dt.date >= start_date) & (df_brut['Timestamp'].dt.date <= end_date)
    # df_brut['Timestamp'].dt.date = extrait JUSTE la date (pas l'heure)
    # >= start_date : lignes APRÈS la date de début
    # <= end_date : lignes AVANT la date de fin
    # & = ET logique (les deux conditions doivent être vraies)
    # Exemple :
    #   Ligne 1 : Timestamp = 2024-12-10, start = 2024-12-10, end = 2025-01-07 → TRUE (incluse)
    #   Ligne 2 : Timestamp = 2024-12-09, start = 2024-12-10, end = 2025-01-07 → FALSE (exclue)
    
    # -------- MASQUE 2 : EVENEMENT --------
    mask_event = df_brut['EventId'].isin(selected_events)
    # isin() = "est dans la liste ?"
    # Exemple :
    #   Ligne 1 : EventId = E27, selected_events = ['E27', 'E13'] → TRUE (E27 est dans la liste)
    #   Ligne 2 : EventId = E21, selected_events = ['E27', 'E13'] → FALSE (E21 n'est pas dans la liste)
    
    # -------- COMBINATION DES DEUX MASQUES --------
    df_filtered = df_brut[mask_date & mask_event]
    # & = ET logique : la ligne doit respecter BOTH conditions pour être incluse
    # Exemple :
    #   Ligne 1 : mask_date=TRUE, mask_event=TRUE → incluse
    #   Ligne 2 : mask_date=TRUE, mask_event=FALSE → exclue
    #   Ligne 3 : mask_date=FALSE, mask_event=TRUE → exclue
    
    # -------- MASQUE 3 : IP (OPTIONNEL) --------
    if selected_ip != "Toutes":
        # Si l'utilisateur A sélectionné une IP spécifique (pas "Toutes")
        df_filtered = df_filtered[df_filtered['SourceIP'] == selected_ip]
        # Filtre ENCORE le DataFrame pour garder que cette IP
    
    # À ce stade, df_filtered contient UNIQUEMENT les lignes qui respectent TOUS les filtres
    
    # ======== AFFICHAGE DES RÉSULTATS ========
    st.markdown("---")
    # Affiche une ligne horizontale (séparateur visuel)
    
    # -------- SÉCURITÉ : TABLEAU VIDE ? --------
    if df_filtered.empty:
        st.warning("⚠️ Aucune donnée ne correspond à vos filtres.")
        # Si aucune ligne ne correspond, affiche un message d'alerte (jaune)
    else:
        # Sinon (si des données existent)
        
        # -------- KPIs (INDICATEURS CLÉS) --------
        col1, col2, col3 = st.columns(3)
        # Crée 3 colonnes de largeur égale côte à côte
        
        with col1:
            # Contenu DANS la première colonne
            st.metric(
                "Total Logs (Filtrés)",
                # Label
                df_filtered.shape[0]
                # shape[0] = nombre de LIGNES
                # Exemple : 655147
            )
        
        with col2:
            # Contenu DANS la deuxième colonne
            pourcentage = (len(df_filtered) / len(df_brut)) * 100
            # len() = compte le nombre de lignes
            # len(df_filtered) / len(df_brut) = ratio
            # * 100 = conversion en pourcentage
            # Exemple : 655147 / 655147 * 100 = 100.0%
            st.metric("% du Dataset", f"{pourcentage:.1f}%")
            # f"...{pourcentage:.1f}%" = formatage chaîne
            # :.1f = affiche 1 seul chiffre après la virgule
            # Exemple : 100.0% (pas 100.000001%)
        
        with col3:
            # Contenu DANS la troisième colonne
            st.metric(
                "IPs Uniques",
                df_filtered['SourceIP'].nunique()
                # nunique() = nombre de VALEURS UNIQUES
                # Exemple : 1129 IPs différentes
            )
        
        # -------- TABLEAU DE DONNÉES --------
        st.subheader("📋 Logs Filtrés")
        # Sous-titre
        st.dataframe(
            df_filtered,
            # Le DataFrame à afficher
            use_container_width=True
            # Le tableau utilise 100% de la largeur disponible
        )
        # Affiche un tableau interactif (scrollable, triable par colonne)
        
        # -------- VISUALISATIONS --------
        st.markdown("---")
        st.header("📊 Analyse Visuelle")
        
        # Crée 2 colonnes pour 2 graphiques côte à côte
        chart_col1, chart_col2 = st.columns(2)
        
        # -------- GRAPHIQUE 1 : TOP 10 IPS --------
        with chart_col1:
            st.subheader("Top 10 IPs Attaquantes")
            top_ips = df_filtered['SourceIP'].value_counts().head(10)
            # value_counts() = compte les occurrences de chaque valeur
            # Exemple résultat :
            #   173.234.31.186      45000
            #   183.129.154.138     40000
            #   ...
            # head(10) = garder seulement les 10 premières
            st.bar_chart(top_ips)
            # Affiche un bar chart (graphique en barres)
        
        # -------- GRAPHIQUE 2 : TIME SERIES --------
        with chart_col2:
            st.subheader("Volume d'attaques par Heure")
            time_series = df_filtered.set_index('Timestamp').resample('H').size()
            # set_index('Timestamp') = utilise Timestamp comme index (pour le regroupement temporel)
            # resample('H') = regroupe par HEURE (H = hour)
            # .size() = compte le nombre de lignes dans chaque groupe
            # Exemple résultat :
            #   2024-12-10 00:00:00    1200 (1200 attaques entre 00h et 01h)
            #   2024-12-10 01:00:00    950
            #   ...
            st.line_chart(time_series)
            # Affiche un line chart (graphique en courbe)
        
        # -------- GRAPHIQUE 3 : TOP USERNAMES --------
        st.markdown("---")
        st.subheader("🚨 Top Usernames Tentés")
        top_users = df_filtered['User'].value_counts().head(10)
        # Même logique que top_ips (mais avec les noms d'utilisateurs)
        # Exemple : root (400k tentatives), admin (5k), support (200), ...
        st.bar_chart(top_users)

# ======== POINT D'ENTRÉE ========
if __name__ == "__main__":
    # Cette condition = "si ce fichier est lancé directement (pas importé ailleurs)"
    main()
    # Appelle la fonction principale
```

---

## 5. DÉPLOIEMENT ET PRODUCTION

### 5.1 Préparation GitHub

**Commandes Git (dans le dossier ssh_monitor) :**

```bash
# 1. Initialiser Git localement
git init
# Crée un dépôt Git caché (.git)

# 2. Ajouter tous les fichiers
git add .
# Stocke les fichiers modifiés en "staging area"

# 3. Créer un commit (snapshot)
git commit -m "Ajout Bonus Upload + Version Finale"
# Sauvegarde les changements avec un message descriptif

# 4. Envoyer sur GitHub
git push
# Synchronise le dépôt local avec GitHub (si un remote est configuré)
```

**Structure du commit :**
```
ssh_monitor/
├── app.py (code source)
├── requirements.txt (dépendances)
├── .gitignore (fichiers ignorés)
├── datasetssh.csv (données)
└── ... (autres fichiers)
```

### 5.2 Déploiement sur Streamlit Cloud

1. Aller sur https://share.streamlit.io/
2. Cliquer "New app"
3. Remplir le formulaire :
   - **Repository :** Yassine-Bouzidi/Analyse-Logs-SSH
   - **Branch :** main
   - **Main file path :** project/ssh_monitor/app.py
   - **App URL :** dashboard-ssh-ysn
4. Cliquer "Deploy!"

**Résultat :** L'app est en ligne à https://dashboard-ssh-ysn.streamlit.app

### 5.3 Déploiement Continu (CI/CD)

Chaque fois que vous faites `git push` :
1. GitHub reçoit le nouveau code
2. Streamlit Cloud détecte le changement (via webhook)
3. L'app est reconstruite automatiquement (environ 1 min)
4. La version en ligne se met à jour

C'est l'avantage du déploiement continu : zéro downtime, mise à jour instantanée.

---

## 6. RÉSULTATS ET MÉTRIQUES

### Performance
- **Temps de chargement initial :** ~3 secondes (première fois)
- **Temps de chargement après cache :** <100ms (5ème clic)
- **Volume de données traité :** 655 147 logs
- **Nombre de colonnes :** 5 (Timestamp, EventId, SourceIP, User, Raw_Message)
- **Nombre d'IPs uniques :** 1 129
- **Nombre d'EventId uniques :** ~10 types d'attaques

### Utilisation Réelle
- **Filtrage par date :** Réduit le dataset de 10% à 100% selon la plage
- **Filtrage par EventId :** Réduit de 5% à 100%
- **Filtrage par IP :** Réduit de 0.1% à 5%
- **Combinaison des filtres :** Réduit le dataset de façon EXPONENTIELLE

Exemple : (50% des dates) × (30% des EventId) × (0.5% d'une IP) = 0.075% du dataset original

---

## 7. AMÉLIORATIONS FUTURES (Roadmap)

### V2 : Fonctionnalités Avancées
1. **Géolocalisation** : Afficher une carte avec les adresses IP et leurs localisations
2. **Export PDF** : Bouton pour télécharger un rapport filtré
3. **Authentification** : Sécuriser l'accès avec login/password (via `st.secrets`)
4. **Real-time Updates** : Intégration avec une API pour les logs live
5. **Alertes** : Notifications email si une IP dépasse X tentatives
6. **Machine Learning** : Détection d'anomalies (comportement anormal)

### Infrastructure
1. **Base de données** : Passer de CSV à PostgreSQL pour plus de performance
2. **Scalabilité** : Migrer de Streamlit Cloud vers Kubernetes (si trafic augmente)
3. **Backup** : Sauvegardes automatiques des logs en cloud

---

## 8. CONCLUSION

Ce projet démontre une **maîtrise complète du cycle de développement** :
- ✅ Analyse de données (Pandas, ETL)
- ✅ Développement d'interface (Streamlit)
- ✅ Déploiement en production (GitHub, Cloud)
- ✅ Optimisation (Cache, Performance)
- ✅ Documentation et communication

Le livrable est **prêt pour un SOC (Security Operations Center) réel** et peut accélérer la détection de menaces.

---

## ANNEXES

### Glossaire Technique
- **ETL** : Extract (extraire), Transform (transformer), Load (charger)
- **DataFrame** : Table de données en mémoire (colonne + lignes)
- **Cache** : Stockage temporaire en mémoire pour éviter recalcul
- **Masque booléen** : Tableau True/False pour filtrer les lignes
- **CI/CD** : Continuous Integration / Continuous Deployment (automatisation)
- **SOC** : Security Operations Center (équipe de sécurité)

### Ressources
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Pandas User Guide](https://pandas.pydata.org/docs/)
- [Git Tutorial](https://git-scm.com/doc)
- [GitHub Pages](https://github.com/)

---

**Fin du rapport**

*Document créé le 8 Décembre 2025 - Yassine Bouzidi*