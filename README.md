# 📊 Application Web Interactive - Analyse de Données avec Streamlit & DuckDB

## 📋 Présentation du projet

Cette application web permet d'analyser des données de ventes (Walmart) et de véhicules électriques à travers une interface interactive développée avec Streamlit. Les données sont stockées et interrogées via DuckDB pour des performances optimales.

### 🎯 Fonctionnalités principales
- 📤 Téléversement de fichiers CSV
- 🗄️ Stockage et requêtes avec DuckDB
- 📊 4 visualisations de KPI interactives
- 🔍 Filtres dynamiques (date, région, produit)

---

## 🛠️ Installation

### Prérequis
- Python 3.9 ou supérieur
- Git

### Étapes d'installation

1. **Cloner le dépôt**
```bash
git clone https://github.com/najoua-elmansouf/streamlit-duckdb-kpis.git
cd streamlit-duckdb-kpis
```

2. **Créer un environnement virtuel (recommandé)**
```bash
python -m venv venv

# Sur Windows
venv\Scripts\activate

# Sur Mac/Linux
source venv/bin/activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

---

## 🚀 Lancement de l'application
```bash
streamlit run APP/app.py
```

L'application s'ouvrira automatiquement dans votre navigateur à l'adresse : `http://localhost:8501`

---

## 📊 Utilisation

1. **Téléverser un fichier CSV** via l'interface
2. **Sélectionner les filtres** (date, région, produit)
3. **Visualiser les 4 KPI** automatiquement générés
4. **Interagir** avec les graphiques pour explorer les données

---

## 👥 Répartition des tâches

| Membre | Rôle | Responsabilités |
|--------|------|-----------------|
| **Najoua** | Chef de projet & Git | - Création du dépôt GitHub<br>- Gestion des branches et merges<br>- Coordination de l'équipe<br>- Résolution des conflits Git |
| **Abdbassit** | Base de données & DuckDB | - Analyse et nettoyage des datasets<br>- Création de la base DuckDB<br>- Import des données CSV<br>- Écriture des requêtes SQL pour les KPI |
| **Hajar** | Interface Streamlit & Upload | - Développement de l'interface utilisateur<br>- Implémentation du téléversement CSV<br>- Création des filtres dynamiques<br>- Connexion Streamlit-DuckDB |
| **Masis** | Visualisations & KPI | - Création des 4 visualisations distinctes<br>- Design des graphiques interactifs<br>- Optimisation de la lisibilité<br>- Tests des visualisations |
| **Mohammed** | Documentation & Tests | - Rédaction du README.md<br>- Tests fonctionnels de l'application<br>- Documentation technique<br>- Rapport de bugs et corrections |

---

## 📂 Structure du projet
```
streamlit-duckdb-kpis/
├── APP/
│   ├── app.py              # Application principale Streamlit
│   └── ...
├── data/
│   └── ...                 # Données et datasets
├── sql/
│   └── ...                 # Requêtes SQL
├── README.md               # Ce fichier
├── requirements.txt        # Dépendances Python
└── .gitignore
```

---

## 🔍 Tests effectués

- ✅ Téléversement de fichiers CSV
- ✅ Stockage dans DuckDB
- ✅ Affichage des 4 KPI
- ✅ Fonctionnement des filtres
- ✅ Responsive design
- ✅ Performance sur grands datasets

---

## 📚 Technologies utilisées

- **Streamlit** : Framework d'interface web
- **DuckDB** : Base de données analytique
- **Pandas** : Manipulation de données
- **Plotly/Matplotlib** : Visualisations
- **Python 3.9+**

---

## 📧 Contact

Pour toute question concernant ce projet :
- **Email** : axel@logbrain.fr
- **GitHub** : [najoua-elmansouf/streamlit-duckdb-kpis](https://github.com/najoua-elmansouf/streamlit-duckdb-kpis)

---

## 📝 License

Projet académique - MBA ESG - Évaluation Management Opérationnel