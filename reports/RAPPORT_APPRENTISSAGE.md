# Rapport d'Apprentissage Python - Brief Pipeline d'Analyse de Logs SSH

---

## 📚 Contexte du Projet

Dans le cadre de ma formation en cybersécurité, j'ai développé un pipeline complet d'analyse de logs SSH pour détecter et visualiser des attaques par force brute sur un serveur critique. Ce projet m'a permis d'acquérir des compétences en Python pour le traitement de données et la création de rapports SOC.

---

## 🎯 Objectifs d'Apprentissage

L'objectif principal était de maîtriser la chaîne de traitement de la donnée de sécurité : **Collecte → Parsing → Normalisation → Analyse → Reporting**.

### Compétences Techniques Visées
1. Manipulation de fichiers texte et CSV en Python
2. Utilisation des expressions régulières (regex) pour le parsing
3. Analyse de données avec Pandas
4. Création de visualisations avec Matplotlib/Seaborn
5. Utilisation de Jupyter Notebook pour la présentation d'analyses

### Compétences SOC
1. Identification de patterns d'attaques SSH
2. Analyse de logs de sécurité
3. Création de rapports d'incident
4. Formulation de recommandations de durcissement

---

## 🚀 Fonctionnalités Clés

- **Parsing Avancé** : Analyse de 55 types d'événements SSH différents (authentification, erreurs réseau, tentatives d'intrusion).
- **Gestion Intelligente des Dates** : Détection automatique des changements d'année (ex: passage de déc. 2024 à janv. 2025) pour une chronologie exacte, même sur des logs à cheval sur deux années.
- **Zéro Faux Négatifs** : Système d'identification exhaustif atteignant **0% de logs "UNKNOWN"** grâce à un moteur d'expressions régulières (Regex) itératif et optimisé.
- **Détection des Menaces** : Identification précise des attaques par force brute, des utilisateurs invalides et des anomalies de protocole (ex: *Bad packet length*, *Corrupted MAC*).
- **Rapports Automatisés** : Génération de rapports CSV détaillés pour l'analyse approfondie et d'un résumé exécutif affiché en console avec les statistiques clés (Top attaquants, volumétrie).

---

## 📖 Apprentissages Python par Phase

### Phase 1 : ETL et Scripting Python

#### Concepts Appris
**1. Manipulation de Fichiers**
Lecture de fichiers ligne par ligne:

with open('SSH.txt', 'r', encoding='utf-8') as f:
for line in f:


# Traitement
**Apprentissage** : J'ai découvert l'importance du gestionnaire de contexte `with` pour gérer automatiquement la fermeture des fichiers et éviter les fuites mémoire.

**2. Expressions Régulières (Regex)**
import re
ip_pattern = r'from\s+(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})'
match = re.search(ip_pattern, message)

**Apprentissage** : Les regex sont puissantes pour extraire des patterns dans du texte non structuré. J'ai appris :
- Les groupes de capture `( )`
- Les quantificateurs `+`, `*`, `{n,m}`
- Les raw strings `r''` pour éviter l'échappement excessif
- La différence entre `.search()` et `.match()`

**3. Structures de Données**
Dictionnaires pour organiser les données
event_patterns = {
'E9': r'Failed password for (?!invalid user).+',
'E10': r'Failed password for invalid user .+'
}

**Apprentissage** : Les dictionnaires Python sont idéaux pour mapper des clés (EventId) à des valeurs (patterns regex). J'ai compris l'importance de structurer les données dès la conception.

**4. Module CSV**
import csv
with open('output.csv', 'w', newline='', encoding='utf-8') as f:
writer = csv.DictWriter(f, fieldnames=['Timestamp', 'EventId'])
writer.writeheader()
writer.writerows(results)

**Apprentissage** : Le paramètre `newline=''` est crucial sous Windows pour éviter les lignes vides. J'ai appris la différence entre `csv.writer` et `csv.DictWriter`.

**5. Gestion des Dates**
from datetime import datetime
timestamp = datetime.strptime('Dec 10 06:55:46 2025', '%b %d %H:%M:%S %Y')

**Apprentissage** : Les formats de date peuvent être complexes. J'ai découvert les directives `strptime` (%b, %d, %H, etc.) pour parser des dates en différents formats.

#### Difficultés Rencontrées

**Problème 1 : FileNotFoundError**
- **Erreur** : Le script ne trouvait pas `SSH.txt` malgré sa présence
- **Cause** : Différence entre le répertoire de travail et l'emplacement du fichier
- **Solution** : Utilisation de `os.path.dirname(__file__)` pour des chemins relatifs robustes

**Problème 2 : SyntaxError avec raw strings**
- **Erreur** : `unterminated string literal` avec les chemins Windows
- **Cause** : Raw strings ne peuvent pas se terminer par un backslash seul
- **Solution** : Utilisation de slashes `/` ou double backslash `\\`

**Problème 3 : Patterns Regex trop génériques**
- **Erreur** : EventId E9 capturait aussi E10
- **Cause** : Regex mal ordonnées et patterns qui se chevauchent
- **Solution** : Ordre de priorité explicite et negative lookahead `(?!invalid user)`

**Problème 4 : Persistance de logs "UNKNOWN"**
- **Erreur** : 1957 lignes (0.3%) classées comme inconnues, masquant potentiellement des attaques.
- **Cause** : Patterns regex trop stricts (ex: espaces manquants) et événements non prévus (erreurs Java/JCraft, problèmes de protocole).
- **Solution** : 
  1. Analyse itérative des messages rejetés.
  2. Création de 20 nouveaux patterns (E28-E55).
  3. Flexibilisation des regex avec `\s+`.
  4. Résultat : **0 log inconnu (100% de couverture)**.

---

### Phase 2 : Jupyter Notebook et Environnement de Travail

#### Concepts Appris

**1. Installation de Packages**
python -m pip install pandas matplotlib seaborn jupyter


**Apprentissage** : J'ai compris la différence entre `pip install` et `python -m pip install` (plus fiable pour garantir l'installation dans le bon environnement Python).

**2. Cellules Markdown vs Code**

**Apprentissage** : Jupyter permet d'alterner entre :
- **Cellules Markdown** : Documentation, titres, explications (storytelling)
- **Cellules Code** : Exécution de Python avec résultats affichés

Cette séparation est idéale pour créer des rapports SOC lisibles et reproductibles.

**3. Kernels et Environnements**

**Apprentissage** : VS Code peut avoir plusieurs environnements Python. J'ai appris à :
- Vérifier le kernel actif en haut à droite du notebook
- Installer les packages dans le bon environnement
- Utiliser `!pip install` directement dans une cellule Jupyter

#### Difficultés Rencontrées

**Problème 1 : ModuleNotFoundError pour pandas**
- **Erreur** : `No module named 'pandas'`
- **Cause** : Packages installés dans un environnement Python différent du kernel Jupyter
- **Solution** : Installation dans le kernel actif ou sélection du bon kernel

**Problème 2 : Cellule Markdown interprétée comme Code**
- **Erreur** : `SyntaxError: invalid syntax` sur du texte Markdown
- **Cause** : Type de cellule incorrect (Python au lieu de Markdown)
- **Solution** : Conversion en Markdown avec le menu déroulant ou raccourci `M`

---

### Phase 3 : Analyse de Données avec Pandas et Visualisation

#### Concepts Appris

**1. DataFrames Pandas**
df = pd.read_csv('datasetssh.csv')
df.head() # Aperçu
df.shape # Dimensions
df.info() # Types de colonnes

**Apprentissage** : Les DataFrames sont comme des tableaux Excel en Python. J'ai découvert des méthodes puissantes pour explorer rapidement les données.

**2. Conversion de Types**
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df['Hour'] = df['Timestamp'].dt.hour

**Apprentissage** : Pandas gère automatiquement les dates avec `.dt` accessor. Cela simplifie énormément l'analyse temporelle.

**3. Agrégations et Comptages**
top_ips = df['SourceIP'].value_counts().head(5)
root_attacks = df[df['User'] == 'root'].shape

**Apprentissage** : `.value_counts()` est incroyablement utile pour compter les occurrences. Le filtrage avec `df[condition]` est intuitif.

**4. Visualisations avec Matplotlib**
plt.figure(figsize=(14, 6))
plt.bar(x, y, color='crimson')
plt.xlabel('Label')
plt.title('Titre')
plt.show()

**Apprentissage** : Matplotlib suit une logique de "peinture" successive. J'ai appris à :
- Définir la taille avec `figsize`
- Personnaliser les couleurs et styles
- Ajouter des labels et titres
- Afficher avec `.show()`

**5. Pie Charts**
plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)

**Apprentissage** : Les pie charts sont efficaces pour montrer des proportions. Le paramètre `autopct` affiche automatiquement les pourcentages.

#### Difficultés Rencontrées

**Problème 1 : Valeurs NaN dans les colonnes**
- **Erreur** : Certaines IPs ou utilisateurs étaient `NaN`
- **Cause** : Regex ne captaient pas tous les formats de logs
- **Solution** : Patterns regex améliorés et gestion des cas manquants

**Problème 2 : Graphiques pas affichés dans Jupyter**
- **Erreur** : Code exécuté mais pas de graphique visible
- **Cause** : Oubli de `plt.show()` ou mauvaise configuration du backend
- **Solution** : Ajout systématique de `.show()` et configuration inline

---

## 🛠️ Ressources Utilisées

### Documentation Officielle
1. **Python Docs** : https://docs.python.org/3/
   - Module `re` (regex)
   - Module `csv`
   - Module `datetime`

2. **Pandas Documentation** : https://pandas.pydata.org/docs/
   - Getting Started Guide
   - API Reference pour DataFrame
   - Time Series / Date functionality

3. **Matplotlib Documentation** : https://matplotlib.org/stable/
   - Pyplot Tutorial
   - Gallery d'exemples

4. **Jupyter Documentation** : https://jupyter-notebook.readthedocs.io/
   - Installation guide
   - Markdown cells

### Tutoriels et Articles
1. **Real Python** : Tutoriels sur regex, pandas, et matplotlib
2. **Stack Overflow** : Résolution de problèmes spécifiques (FileNotFoundError, SyntaxError)
3. **GeeksforGeeks** : Exemples de code pour value_counts(), to_datetime()

### Outils de Développement
1. **VS Code** : Éditeur avec extension Jupyter
2. **PowerShell** : Terminal pour exécution des scripts
3. **Git** : Versioning du code (recommandé pour la suite)

---

## 💡 Compétences Acquises

### Compétences Techniques Python

| Compétence |
|------------|
| Manipulation de fichiers | 
| Expressions régulières |
| Pandas DataFrames |
| Visualisation (Matplotlib) |
| Jupyter Notebook |

### Compétences SOC

- **Analyse de logs** : Capacité à parser et interpréter des logs SSH
- **Détection de menaces** : Identification de patterns d'attaques par force brute
- **Reporting** : Création de rapports visuels pour stakeholders
- **Recommandations** : Formulation de mesures de durcissement pertinentes

---

## 🔄 Méthodologie de Travail

### Approche Itérative

J'ai adopté une approche **itérative** pour ce projet :

1. **Version 1** : Script basique qui lit les fichiers
2. **Version 2** : Ajout du parsing regex simple
3. **Version 3** : Amélioration des patterns et gestion des erreurs
4. **Version 4** : Optimisation et ajout de statistiques
5. **Version 5** : Intégration Jupyter et visualisations

### Debugging Méthodique

Pour chaque erreur rencontrée :
1. **Lecture du message d'erreur** (ligne, type d'erreur)
2. **Isolation du problème** (test sur un échantillon réduit)
3. **Recherche de solutions** (documentation, Stack Overflow)
4. **Test de la correction**
5. **Documentation de la solution** (commentaires dans le code)

### Test et Validation

- Test sur les **5 premières lignes** avant de traiter l'ensemble
- Vérification des **outputs intermédiaires** (print statements)
- Validation des **résultats** avec des calculs manuels sur un échantillon

---

## 📈 Évolution et Prochaines Étapes

### Points Forts du Projet
✅ Pipeline ETL fonctionnel et robuste  
✅ Code bien commenté et structuré  
✅ Visualisations claires et pertinentes  
✅ Rapports exploitables pour SOC  

### Axes d'Amélioration
🔄 Ajouter des tests unitaires (pytest)  
🔄 Gérer des formats de logs multiples (Apache, Nginx, etc.)  
🔄 Créer une interface web (Flask/Streamlit)  
🔄 Automatiser avec des scripts cron  
🔄 Intégrer avec des SIEM (Splunk, ELK)  

### Compétences à Approfondir
📚 Machine Learning pour détection d'anomalies  
📚 API REST pour exposer les résultats  
📚 Docker pour conteneurisation du pipeline  
📚 Bases de données (PostgreSQL) pour stocker les logs  

---

## CODE DÉTAILLÉ AVEC EXPLICATIONS

### Initialisation et Chargement
```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Imports : Tu charges pandas (pour manipuler les tableaux de données), matplotlib et seaborn (pour créer les graphiques).
# Warnings : warnings.filterwarnings('ignore') est une astuce pour garder ton notebook propre. Cela empêche Python d'afficher des avertissements rouges (souvent liés à des mises à jour futures de bibliothèques) qui ne bloquent pas le code mais polluent l'affichage.
```

```python
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', None)
df = pd.read_csv('data/datasetssh.csv')
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (12, 6)
print(f"📊 Dataset : {df.shape[0]} lignes × {df.shape[1]} colonnes\n")

# Settings : Tu configures pandas pour afficher jusqu'à 100 lignes et toutes les colonnes (utile si ton écran est large). Tu définis aussi la taille par défaut des graphiques (12x6).
# Chargement : read_csv charge ton fichier de logs dans la variable df (DataFrame). C'est maintenant ton tableau Excel virtuel.
# sns.set_style('whitegrid') : Ajoute une grille blanche en fond de graphique (plus lisible et pro).
# figure.figsize : Définit une taille d'image par défaut (12x6) assez large pour être lisible.
# Vérification : df.shape te donne immédiatement la taille (nombre de lignes = nombre de logs, colonnes = infos extraites). C'est le premier réflexe d'un Data Analyst pour vérifier que le chargement a fonctionné.
```

### Inspection des Anomalies (Unknown)
```python
unknown_logs = df[df['EventId'] == 'UNKNOWN']

# Filtrage : Tu crées un sous-tableau unknown_logs qui ne contient que les lignes où l'ID de l'événement n'a pas été reconnu par ton script précédent.
# Investigation : Si tu en as (len > 0), tu affiches les messages bruts (Raw_Message) et les IPs sources.
# Pourquoi c'est important ? En cybersécurité, un log "inconnu" peut être soit une erreur de parsing (ton script a mal lu la ligne), soit une nouvelle méthode d'attaque que tu ne connais pas encore.
```

### Traitement Temporel (Time Series)

```python
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df['Hour'] = df['Timestamp'].dt.hour
df['Minute'] = df['Timestamp'].dt.minute
df['Date'] = df['Timestamp'].dt.date

# Conversion : Par défaut, les dates dans un CSV sont lues comme du texte. pd.to_datetime les convertit en objets datetime intelligents.
# Extraction : Tu crées de nouvelles colonnes (Hour, Minute) pour faciliter l'analyse par heure plus tard. Cela te permettra de répondre à la question : "À quelle heure les pirates attaquent-ils le plus ?".
```

###  Analyse des Attaquants (Top IPs)

```python
top_ips = df['SourceIP'].value_counts().head(5)

# Comptage : value_counts() compte combien de fois chaque IP apparaît et les trie par ordre décroissant.
# Calcul de fréquence : (count / len(df)) * 100 calcule quel pourcentage du trafic total représente chaque attaquant. C'est vital pour prioriser : si une seule IP fait 43% des attaques, c'est ta cible prioritaire à bloquer.
```

### Analyse des Cibles (Utilisateurs & Root)

```python
root_attacks = df[df['User'] == 'root'].shape[0]
total_with_user = df['User'].notna().sum()

# Focus Root : Tu filtres le tableau pour ne garder que les lignes où l'utilisateur est "root". .shape[0] compte le nombre de lignes résultantes.
# Remplissage : df['User'].notna().sum() compte combien de logs ont un utilisateur identifié (contrairement à ceux où c'est juste une connexion technique sans user).
```

### Analyse des Types d'Attaques (EventId)

```python
event_counts = df['EventId'].value_counts()

# Distribution : Permet de voir comment on t'attaque. Est-ce surtout du "Failed password" (force brute) ou du "Invalid user" (dictionnaire d'utilisateurs) ?
# Visualisation texte : La ligne bar = "█" * int(percentage) est une astuce sympa pour faire un mini-graphique directement dans la console textuelle.
```

### Visualisation Graphique (Data Viz)

**Graphique 1 : Bar Chart (Top IPs)**
```python
bars = plt.bar(range(len(top_10_ips)), top_10_ips.values, color='crimson'...)

# Choix du graph : Un diagramme en barres est idéal pour comparer des quantités (nombre d'attaques) entre différentes catégories (IPs).
# Couleur : 'crimson' (rouge sang) est choisi pour rappeler le danger/l'alerte.
# Annotations : La boucle for avec plt.text ajoute le chiffre exact au-dessus de chaque barre, ce qui rend le graph lisible même sans regarder l'axe Y.
```

**Graphique 2 : Pie Chart (Camembert des événements)**
```python
if others > 0:
    pie_data = pd.concat([top_5_events, pd.Series({'Autres': others})])
else:
    pie_data = top_5_events

wedges, texts, autotexts = plt.pie(pie_data.values, labels=pie_data.index, ...)

# La Préparation (pd.concat): C'est l'étape de calcul. Python trie tes données brutes (qui sont trop nombreuses et illisibles) pour créer un petit groupe propre : les 5 événements principaux + une catégorie "Autres".

# Résultat : Une liste de données prête à l'emploi.

# La Présentation (plt.pie et explode): C'est l'étape de dessin. Python prend la liste propre préparée juste avant et génère l'image du camembert. C'est ici qu'on ajoute l'option explode pour écarter les parts et rendre le graphique joli.

# Résultat : L'image finale du graphique.
```

**Graphique 3 : Line Chart (Chronologie)**
```python
attacks_per_hour = df.groupby('Hour').size()
plt.plot(..., color='darkred')
plt.fill_between(...)

# Groupby : Tu regroupes les données par heure (0h, 1h... 23h) et tu comptes la taille (size) de chaque groupe.

# Rendu : fill_between colorie la zone sous la courbe, ce qui donne un effet de volume à l'attaque. Cela permet de voir s'il y a eu un pic soudain (attaque scriptée massive) ou si c'est constant.
```

## 🎓 Conclusion

Ce brief m'a permis de développer des compétences solides en Python pour l'analyse de données de sécurité. J'ai appris à :

1. **Automatiser** des tâches répétitives de parsing de logs
2. **Structurer** des données non structurées avec des regex
3. **Analyser** des volumes importants de données avec Pandas
4. **Communiquer** des résultats techniques via des visualisations
---
