# Pipeline d’Analyse de Logs SSH – Investigation SOC & MonitorSSH

## 📋 Description

Ce projet met en place un pipeline ETL complet pour analyser des logs SSH dans un contexte SOC (Security Operations Center), depuis des fichiers bruts jusqu’à un dashboard interactif.  
Il permet d’identifier les tentatives d’attaques (notamment par force brute), de visualiser les comportements suspects et de produire des rapports exploitables pour les équipes de sécurité.  

En plus du notebook d’analyse, le projet inclut une application web **Streamlit** nommée **MonitorSSH**, qui transforme le dataset en un outil de monitoring accessible depuis un navigateur.

## 🎯 Objectifs

- Automatiser l’extraction, la normalisation et l’enrichissement de logs SSH bruts (pipeline ETL).  
- Identifier les adresses IP malveillantes, les utilisateurs ciblés et les patterns d’attaque récurrents.  
- Visualiser les menaces de sécurité via des graphiques clairs et des métriques SOC.  
- Fournir un **dashboard web interactif** pour les analystes, sans besoin d’ouvrir un notebook.  

## 📁 Structure du projet

project/
├── data/
│ ├── SSH.txt # Logs SSH bruts (2000 lignes)
│ └── datasetssh.csv # Dataset SSH normalisé (généré)
├── notebooks/
│ └── Investigation_Menaces.ipynb # Notebook d'analyse Jupyter
├── reports/
│ ├── Investigation_Menaces.pdf
│ ├── RAPPORT_APPRENTISSAGE.md
│ └── rapport_monitorssh.md
├── ssh_monitor/
│ ├── app.py # Dashboard Streamlit (MonitorSSH)
│ ├── datasetssh.csv # Dataset d'exemple pour la démo
│ └── requirements.txt # Dépendances de l'application
├── logtocsv.py # Script de parsing / ETL
└── README.md # Documentation du projet


## 🚀 Installation

### Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- Bibliothèque `pandas`, `Jupyter`, `matplotlib`, `seaborn` et `ipkernel`
- Git (pour cloner le dépôt)

### Clonage du dépôt

git clone https://github.com/Yassine-Bouzidi/Analyse-Logs-SSH.git

cd Analyse-Logs-SSH/project

### Installation des Dépendances

Création d’un environnement virtuel (recommandé) :
python -m venv .venv

Linux / macOS:
source .venv/bin/activate

Windows:
..venv\Scripts\activate


Installation des dépendances globales (ETL + analyse) :

pip install pandas matplotlib seaborn jupyter ipykernel


Pour l’application Streamlit, les dépendances spécifiques sont listées dans `project/ssh_monitor/requirements.txt` :

cd ssh_monitor
pip install -r requirements.txt


## 💻 Utilisation

### Étape 1 : Générer le Dataset CSV (ETL)

Exécutez le script de parsing pour convertir les logs bruts en dataset structuré :

cd project
python logtocsv.py


**Sortie principale :**

- Le fichier de sortie normalisé contient les colonnes suivantes :

| Colonne | Description |
| :--- | :--- |
| **Timestamp** | Date et heure normalisées (format `YYYY-MM-DD HH:MM:SS`). |
| **EventId** | Identifiant unique du type d'événement (de E1 à E55). |
| **SourceIP** | Adresse IP d'origine de la connexion (si présente). |
| **User** | Nom d'utilisateur ciblé ou authentifié (si présent). |
| **Raw_Message** | Le message de log original pour audit et vérification. |


- Affichage des statistiques : Top IPs, Top événements, taux de parsing


## 🔧 Détails techniques ETL

### Gestion des logs inconnus

Une attention particulière a été portée à la réduction du bruit : le parser couvre les principales erreurs de protocole SSH, exceptions applicatives et variations syntaxiques, afin de limiter au maximum les événements “UNKNOWN”.  

### Moteur regex et EventIds

Le moteur repose sur un dictionnaire d’expressions régulières permettant de mapper chaque ligne de log à un `EventId` normalisé.  
Les événements critiques incluent notamment les échecs d’authentification, les utilisateurs invalides et les messages de type tentative d’intrusion.


### 📊 Étape 2 : Analyse dans Jupyter Notebook

Lancez Jupyter Notebook pour l'analyse visuelle :

jupyter notebook Investigation_Menaces.ipynb

Le notebook `notebooks/Investigation_Menaces.ipynb` réalise l’analyse exploratoire et visuelle :

1. Chargement du dataset SSH via `pandas`.  
2. Nettoyage et mise en forme des timestamps.  
3. Analyses statistiques :  
   - Top IPs malveillantes.  
   - Utilisateurs les plus ciblés (dont `root`).  
   - Répartition des types d’événements.  
4. Visualisations :  
   - Bar chart des IPs les plus agressives.  
   - Diagrammes de répartition des événements.  
   - Timeline du volume d’attaques dans le temps.  

L’objectif est de fournir à l’analyste SOC une vision claire des tendances d’attaque et des priorités de remédiation.



## 📊 Fonctionnalités du Script `logtocsv.py`

## 🔧 Détails Techniques

### Gestion des Logs Inconnus ("UNKNOWN")
Une grande partie du travail a consisté à réduire le bruit. Initialement confronté à près de 2000 logs non identifiés, le parser a été affiné pour couvrir 100% des cas, incluant :
- Les erreurs de protocole SSH (*MAC corrompu*, *bad packet length*).
- Les exceptions Java/JCraft (*timeouts*, *annulations utilisateur*).
- Les variantes syntaxiques complexes (*Invalid user* avec espaces multiples).

### Moteur Regex
Le projet utilise un dictionnaire de **55 expressions régulières** optimisées.
*Exemple de détection générique pour éviter les faux négatifs :*

### EventIds Critiques

| EventId | Description | Criticité |
|---------|-------------|-----------|
| **E9** | Failed password (utilisateur valide) | 🔴 Haute |
| **E10** | Failed password (utilisateur invalide) | 🔴 Haute |
| **E13** | Invalid user | 🟠 Moyenne |
| **E27** | Reverse DNS failed - POSSIBLE BREAK-IN ATTEMPT | 🔴 Critique |

### Architecture du Code

load_templates() # Charge les patterns d'événements
identify_event() # Identifie l'EventId par regex
extract_ip() # Extrait l'IP source
extract_user() # Extrait l'utilisateur ciblé
parse_ssh_log_line() # Parse une ligne complète
main() # Fonction principale ETL


## 📈 Contenu du Notebook Jupyter

Le notebook `Investigation_Menaces.ipynb` contient :

1. **Chargement des données** : Import du CSV avec pandas
2. **Nettoyage temporel** : Conversion des timestamps
3. **Analyse statistique** :
   - Top 5 des IPs malveillantes
   - Utilisateurs les plus ciblés (notamment root)
   - Répartition des types d'événements
4. **Visualisations** :
   - Bar chart : Top 10 IPs agressives
   - Pie chart : Répartition des événements
   - Timeline : Attaques par heure
5. **Rapport exécutif** : Conclusions et recommandations SOC

## 🔍 Exemple de Résultats

### Top 3 IPs Malveillantes (Exemple)

1- 183.62.140.253 → 867 tentatives (43.4%)

2- 187.141.143.180 → 349 tentatives (17.5%)

3- 103.99.0.122 → 172 tentatives (8.6%)

### Événements les Plus Fréquents
E20 (Auth failure) : 494 occurrences (24.7%)
E24 (Disconnect) : 413 occurrences (20.7%)
E9 (Failed password) : 385 occurrences (19.3%)



## 🌐 Étape 3 – MonitorSSH : Dashboard Streamlit

En complément du notebook, le projet propose une application web **Streamlit** appelée `MonitorSSH`, permettant d’explorer les logs de manière interactive via un navigateur web.

### Lancement en local

Depuis la racine du projet :

cd project/ssh_monitor
pip install -r requirements.txt
streamlit run app.py


### Fonctionnalités principales

- Indicateurs clés (métriques) :
  - Nombre total d’événements.
  - Nombre d’IPs uniques.
  - Volume de tentatives d’authentification échouées.
- Filtres interactifs (dans la barre latérale) :
  - Filtre par `EventId` (type d’événement).
  - Sélection d’IPs spécifiques.
  - Filtrage temporel.
- Graphiques interactifs :
  - Top IPs agressives.
  - Volume d’attaques par heure/jour.
  - Utilisateurs les plus ciblés.

L’application peut être déployée sur **Streamlit Community Cloud** pour obtenir une URL publique partageable avec un responsable ou un recruteur, ce qui est une pratique courante pour les dashboards Streamlit.


## 🛡️ Recommandations de sécurité

À partir des résultats du pipeline et du dashboard, plusieurs actions de sécurité peuvent être proposées :

1. **Blocage immédiat** des IPs les plus agressives au niveau du firewall. 
2. **Désactivation de l'authentification root SSH** (`PermitRootLogin no`)
3. **Implémentation de Fail2Ban** ou équivalent pour bannir automatiquement les IPs en cas de tentatives répétées.
4. **Migration progressive vers l’authentification par clés SSH**.
5. **Changement du port SSH** (22 → port personnalisé)
6. **Intégration de la surveillance SSH dans un IDS/IPS** (Snort, Suricata, etc.).

Ces recommandations sont classiques dans le hardening SSH et la réponse à des attaques par force brute.


## 📚 Technologies utilisées

- **Python 3.x** – Langage principal.  
- **Pandas** – Manipulation et analyse de données.  
- - **Matplotlib** : Création de graphiques
- **Seaborn** : Visualisations statistiques avancées  
- **Jupyter Notebook** – Analyse exploratoire et documentation technique.  
- **Regex (`re`)** – Parsing avancé des logs.  
- **Streamlit** – Développement du dashboard web interactif.  
- **Git / GitHub** – Versionnement et partage du projet.  

L’ensemble de cette stack est typique des projets cybersécurité modernes.


## 👤 Auteur

**Yassine Bouzidi**  
Administrateur solutions cybersécurité  
Formation : Simplon – Pipeline d’Analyse de Logs SSH (2025)

## 📝 Licence

Ce projet est distribué sous licence **MIT**.  
Consultez le fichier `LICENSE` à la racine du dépôt pour plus de détails.

