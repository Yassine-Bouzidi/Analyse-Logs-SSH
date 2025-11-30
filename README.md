# Pipeline d'Analyse de Logs SSH - Investigation SOC

## 📋 Description

Ce projet implémente un pipeline ETL (Extract, Transform, Load) complet pour l'analyse de logs SSH dans un contexte SOC (Security Operations Center). Il permet de détecter et visualiser les tentatives d'attaques par force brute sur un serveur critique.

## 🎯 Objectifs

- **Automatiser** l'extraction et la normalisation de logs SSH bruts
- **Identifier** les adresses IP malveillantes et les patterns d'attaque
- **Visualiser** les menaces de sécurité pour faciliter la prise de décision
- **Produire** des rapports d'analyse exploitables pour les équipes SOC

## 📁 Structure du Projet
project/
├── SSH.txt # Logs SSH bruts (2000 lignes)
├── openssh-2k-log-templates-xxx.csv # Templates d'événements SSH
├── logtocsv.py # Script de parsing ETL
├── datasetssh.csv # Dataset normalisé (généré)
├── Investigation_Menaces.ipynb # Notebook d'analyse Jupyter
├── README.md # Ce fichier
└── RAPPORT_APPRENTISSAGE.md # Rapport d'apprentissage Python

## 🚀 Installation

### Installation des Dépendances

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- Bibliothèque `pandas`, `Jupyter`, `matplotlib`, `seaborn` et `ipkernel`

pip install pandas matplotlib seaborn jupyter ipykernel


## 💻 Utilisation

### Étape 1 : Générer le Dataset CSV

Exécutez le script de parsing pour convertir les logs bruts en dataset structuré :

python logtocsv.py


**Sortie attendue :**

- Le fichier de sortie normalisé contient les colonnes suivantes :

| Colonne | Description |
| :--- | :--- |
| **Timestamp** | Date et heure normalisées (format `YYYY-MM-DD HH:MM:SS`). |
| **EventId** | Identifiant unique du type d'événement (de E1 à E55). |
| **SourceIP** | Adresse IP d'origine de la connexion (si présente). |
| **User** | Nom d'utilisateur ciblé ou authentifié (si présent). |
| **Raw_Message** | Le message de log original pour audit et vérification. |


- Affichage des statistiques : Top IPs, Top événements, taux de parsing

### Étape 2 : Analyse dans Jupyter Notebook

Lancez Jupyter Notebook pour l'analyse visuelle :

jupyter notebook Investigation_Menaces.ipynb


Ou ouvrez le fichier `.ipynb` directement dans VS Code avec l'extension Jupyter.

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


## 🛡️ Recommandations de Sécurité

Sur la base de cette analyse, les recommandations SOC incluent :

1. **Blocage immédiat** des IPs du Top 5 via firewall
2. **Désactivation de l'authentification root SSH** (`PermitRootLogin no`)
3. **Implémentation de Fail2Ban** pour blocage automatique
4. **Migration vers l'authentification par clés SSH**
5. **Changement du port SSH** (22 → port personnalisé)
6. **Déploiement d'un IDS/IPS** (Snort, Suricata)

## 📚 Technologies Utilisées

- **Python 3.x** : Langage de programmation principal
- **Pandas** : Manipulation et analyse de données
- **Matplotlib** : Création de graphiques
- **Seaborn** : Visualisations statistiques avancées
- **Jupyter Notebook** : Environnement d'analyse interactif
- **Regex (re)** : Parsing de logs avec expressions régulières

## 👤 Auteur

**Yassine Bouzidi**  
Administrateur Solutions cybersécurité  
Formation : Simplon - Pipeline d'Analyse de Logs SSH  
Date : 21/22 Novembre 2025

## 📝 Licence

Ce projet est développé dans un cadre pédagogique pour la formation en cybersécurité.

## 🤝 Contribution

Pour toute question ou amélioration, n'hésitez pas à ouvrir une issue ou soumettre une pull request.

## 📞 Support

Pour toute assistance technique :
- Consultez la documentation inline dans `logtocsv.py`
- Référez-vous au notebook Jupyter pour des exemples d'utilisation
- Consultez le rapport d'apprentissage pour comprendre la démarche

