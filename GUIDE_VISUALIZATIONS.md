# 📊 Guide des Visualisations de Distribution

## Pourquoi 4 types différents ?

Chaque type de graphique répond à une **question business différente** :

---

## 1. 📦 Box Plot (Holiday)

### Question Business:
> **"Les ventes sont-elles significativement différentes pendant les jours fériés ?"**

### Ce que ça montre:
- **Boîte**: 50% des ventes centrales (entre 25% et 75%)
- **Ligne du milieu**: Médiane (valeur du milieu)
- **Moustaches**: Min et max (sans outliers)
- **Points**: Valeurs extrêmes (exceptionnellement hautes ou basses)

### Exemple d'insight:
- Si la boîte "Holiday" est plus haute → Les ventes augmentent pendant les fêtes
- Si les boîtes se chevauchent → Pas de grande différence

### Quand l'utiliser:
✅ Comparer 2-3 groupes (Holiday vs Normal)
✅ Identifier les outliers (semaines exceptionnelles)
✅ Voir la médiane (plus robuste que la moyenne)

---

## 2. 🏬 Box Plot (Top Stores)

### Question Business:
> **"Quels stores ont des ventes stables vs volatiles ?"**

### Ce que ça montre:
- Même principe que Box Plot, mais par store
- Compare la **variabilité** entre les meilleurs stores

### Exemple d'insight:
- **Petite boîte** = Ventes prévisibles et stables → Moins de risque
- **Grande boîte** = Ventes variables → Plus de risque mais aussi d'opportunités
- **Points nombreux** = Beaucoup d'anomalies → Nécessite investigation

### Quand l'utiliser:
✅ Évaluer le risque par store
✅ Identifier les stores prévisibles
✅ Trouver les anomalies

---

## 3. 🎻 Violin Plot

### Question Business:
> **"Où se concentrent la majorité des ventes ? Y a-t-il plusieurs pics ?"**

### Ce que ça montre:
- **Largeur du violon** = Densité (combien de fois cette valeur apparaît)
- **Partie large** = Beaucoup de semaines avec ces ventes
- **Partie étroite** = Peu de semaines avec ces ventes

### Exemple d'insight:
- **Un pic** → Distribution normale, ventes cohérentes
- **Deux pics** → Deux modes de fonctionnement (ex: période haute et basse saison)
- **Violon large en bas** → Beaucoup de semaines avec faibles ventes (problème!)

### Quand l'utiliser:
✅ Comprendre la **forme** de la distribution
✅ Détecter les distributions bi-modales (2 pics)
✅ Voir plus de détails que le Box Plot

---

## 4. 📊 Histogram

### Question Business:
> **"Combien de semaines ont des ventes entre X et Y ?"**

### Ce que ça montre:
- **Barres** = Fréquence (nombre de semaines dans chaque plage)
- **Hauteur** = Combien de fois cette plage de ventes apparaît
- **Box plot en haut** = Résumé statistique

### Exemple d'insight:
- **Pic à droite** = Beaucoup de bonnes semaines → Positif!
- **Pic à gauche** = Beaucoup de semaines faibles → Problème
- **Répartition large** = Ventes imprévisibles
- **Répartition étroite** = Ventes consistantes

### Statistiques affichées:
- **Moyenne**: Somme / nombre de semaines
- **Médiane**: Valeur du milieu (50%)
- **Asymétrie**: 
  - Moyenne > Médiane (➡️) = Quelques très grosses semaines tirent la moyenne vers le haut
  - Moyenne < Médiane (⬅️) = Quelques très faibles semaines tirent la moyenne vers le bas

### Quand l'utiliser:
✅ Voir la **fréquence** de chaque plage de ventes
✅ Identifier la forme de distribution (normale, asymétrique)
✅ Ajuster les bins (plages) pour plus/moins de détail

---

## 🎯 Résumé - Quelle visualisation choisir ?

| Question | Meilleur choix |
|----------|---------------|
| "Y a-t-il une différence Holiday vs Normal ?" | **Box Plot (Holiday)** |
| "Quels stores sont stables ou risqués ?" | **Box Plot (Top Stores)** |
| "Où se concentrent les ventes ?" | **Violin Plot** |
| "Combien de semaines ont X ventes ?" | **Histogram** |
| "Y a-t-il plusieurs modes de fonctionnement ?" | **Violin Plot** |
| "Identifier les outliers rapidement" | **Box Plot** |

---

## 💡 Conseil Pro:

**Utilise plusieurs visualisations ensemble !**

1. Commence par **Histogram** → Vue d'ensemble
2. Passe à **Box Plot** → Compare les groupes
3. Utilise **Violin Plot** → Comprends la densité
4. Analyse les **stores individuels** → Identifie les causes

C'est comme regarder un objet sous différents angles pour le comprendre complètement! 🔍

---

**Créé pour le projet**: streamlit-duckdb-kpis  
**Module**: Visualisations & KPI  
**Date**: Janvier 2026
