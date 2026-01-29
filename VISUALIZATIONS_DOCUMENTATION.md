# 📊 Visualisations & KPI - Documentation

## Responsabilités accomplies ✅

### 1. Créer 4 visualisations différentes
### 2. Connecter chaque graphique aux données filtrées
### 3. Améliorer la lisibilité des graphiques

---

## 📈 Visualisations pour WALMART (Onglet "Analyses Avancées")

### 1. 🏆 Top 10 vs Bottom 10 Stores
- **Type**: Graphique en barres groupées
- **But**: Comparer les meilleurs et pires performers
- **Données**: Ventes totales par store (Top 10 en bleu, Bottom 10 en rouge)
- **Logique Business**: Identifier les stores qui nécessitent attention/amélioration
- **Connexion aux filtres**: Respecte les filtres de stores, dates et holiday_flag

### 2. 🎉 Impact des Jours Fériés par Store
- **Type**: Graphique en barres avec échelle de couleur
- **But**: Mesurer l'impact % des jours fériés sur les ventes par store
- **Données**: Pourcentage d'augmentation (ou diminution) des ventes en période holiday
- **Logique Business**: Identifier quels stores bénéficient le plus des périodes festives
- **Formule**: `((Ventes_Holiday - Ventes_Normal) / Ventes_Normal) * 100`
- **Connexion aux filtres**: Calculé sur les données filtrées

### 3. 📦 Distribution des Ventes (Box Plot)
- **Type**: Boîte à moustaches (Box Plot)
- **But**: Comparer la distribution statistique des ventes (médiane, quartiles, outliers)
- **Données**: Distribution complète des ventes hebdomadaires Holiday vs Non-Holiday
- **Logique Business**: Comprendre la variabilité et identifier les anomalies
- **Connexion aux filtres**: Respecte tous les filtres actifs

### 4. 📈 Tendance: Top 5 Stores
- **Type**: Graphique multi-lignes
- **But**: Suivre l'évolution temporelle des 5 meilleurs stores
- **Données**: Ventes hebdomadaires des Top 5 performers sur la période
- **Logique Business**: Analyser les tendances de croissance/décroissance des leaders
- **Connexion aux filtres**: Données filtrées selon la sélection

---

## 🚗 Visualisations pour ELECTRIC VEHICLES (Onglet "Analyses Avancées")

### 1. ⚡ Autonomie vs Capacité Batterie
- **Type**: Scatter Plot (nuage de points)
- **But**: Analyser la corrélation entre capacité batterie et autonomie
- **Dimensions**: 
  - X: Capacité batterie (kWh)
  - Y: Autonomie (km)
  - Couleur: Segment (SUV, Sedan, etc.)
  - Taille: Vitesse maximale
- **Connexion aux filtres**: Filtré par marques et segments sélectionnés

### 2. 🚙 Comparaison par Segment
- **Type**: Barres groupées
- **But**: Comparer le nombre de modèles et autonomie moyenne par segment
- **Données**: Agrégation par segment (nb_models, avg_range, avg_battery)
- **Connexion aux filtres**: Respecte les filtres de marques et segments

### 3. 🏁 Distribution des Vitesses Max
- **Type**: Histogramme
- **But**: Visualiser la répartition des vitesses maximales
- **Données**: Toutes les vitesses max des véhicules filtrés
- **Connexion aux filtres**: Filtré par marques et segments

### 4. 🎯 Bubble Chart Multi-Dimensions
- **Type**: Graphique à bulles
- **But**: Visualiser simultanément batterie, vitesse et autonomie
- **Dimensions**:
  - X: Capacité batterie (kWh)
  - Y: Vitesse max (km/h)
  - Taille: Autonomie (km)
  - Couleur: Marque
- **Connexion aux filtres**: Top 20 modèles filtrés par autonomie

---

## 🎨 Améliorations de lisibilité

### Schéma de couleurs professionnel
- Palette bleue cohérente (#1E78FF, #5AA9FF)
- Couleurs contrastées pour les comparaisons
- Utilisation de dégradés pour les graphiques en barres

### Interactivité Plotly
- Hover data détaillé sur tous les graphiques
- Zoom et pan activés
- Légendes interactives

### Organisation visuelle
- Grille 2x2 pour présentation équilibrée
- Cards avec bordures et ombres
- Titres descriptifs avec émojis
- Marges optimisées pour lisibilité

### Connexion aux données
- Toutes les requêtes SQL utilisent les paramètres de filtrage
- Utilisation de `UNNEST(?)` pour les listes de filtres
- Gestion appropriée des valeurs NULL
- Agrégations pertinentes (SUM, AVG, COUNT)

---

## 📊 Requêtes SQL créées

### Walmart (Business-Oriented)
- `sql_weekly_perf`: Performance hebdomadaire détaillée par store
- `sql_performance`: Calcul des métriques de performance (total, moyenne, nb semaines)
- `sql_holiday_impact`: Comparaison ventes Holiday vs Non-Holiday par store
- `sql_distribution`: Distribution complète pour analyse statistique

### Electric Vehicles
- `sql_scatter`: Données pour scatter plot multi-dimensions
- `sql_segment`: Agrégation par segment
- `sql_speed_dist`: Distribution des vitesses

---

## 💡 Logique Business des Visualisations

### Pourquoi ces choix pour Walmart?

#### ❌ Évité (pas logique):
- **Température vs Ventes**: Walmart n'est pas sensible aux variations météo comme une glacière
- **Fuel Price vs Ventes**: Impact indirect et minime sur les achats en magasin

#### ✅ Choisi (pertinent):
1. **Top/Bottom Performers**: Identifier rapidement les stores problématiques
2. **Impact Holiday**: Mesurer ROI des promotions de périodes festives
3. **Distribution statistique**: Détecter anomalies et patterns inhabituels
4. **Tendance Top 5**: Suivre les leaders et apprendre de leurs succès

---

## 🚀 Technologies utilisées

- **Plotly Express**: Graphiques basiques (bar, line, pie, histogram)
- **Plotly Graph Objects**: Graphiques avancés (subplots, dual axes)
- **DuckDB**: Requêtes SQL performantes
- **Pandas**: Manipulation de données (pivot, rolling)
- **Streamlit**: Interface et mise en page

---

## ✅ Statut du projet

**Toutes les responsabilités sont complétées:**
- ✅ 4 visualisations différentes créées pour Walmart
- ✅ 4 visualisations différentes créées pour Electric Vehicles
- ✅ Tous les graphiques connectés aux filtres
- ✅ Lisibilité optimisée (couleurs, layout, interactivité)

---

**Développé par**: Équipe Projet  
**Rôle**: 📊 Visualisations & KPI  
**Branche**: masis-feature-Visualisations-&-KPI  
**Date**: Janvier 2026
