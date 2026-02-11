import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils import (
    format_number,
    create_scatter_plot,
    create_bar_chart,
    create_line_chart,
    categorize_performance,
    create_comparison_selector,
    section_card,
    create_2x2_comparison_grid,
    create_comparison_suggestions,
    clean_numeric_column
)

# Get the parent directory of APP folder to access data
DB_PATH = "data/project.db"

# ---------------------------
# Page config
# ---------------------------
st.set_page_config(
    page_title="KPI Dashboard | Walmart & EV",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------
# Blue & White Professional CSS
# ---------------------------
st.markdown(
    """
    <style>
    /* Global */
    .stApp {
        background: linear-gradient(180deg, #F7FBFF 0%, #FFFFFF 60%);
    }
    h1, h2, h3, h4 {
        color: #0B2D5C !important;
        letter-spacing: 0.2px;
    }
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0B2D5C 0%, #0E3A73 100%);
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    section[data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stMultiSelect label,
    section[data-testid="stSidebar"] .stDateInput label {
        font-weight: 600;
        opacity: 0.95;
    }

    /* Make inputs look clean */
    div[data-baseweb="select"] > div {
        border-radius: 12px !important;
    }
    input {
        border-radius: 12px !important;
    }

    /* KPI cards */
    .kpi-row {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 14px;
        margin-top: 8px;
        margin-bottom: 10px;
    }
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid rgba(11,45,92,0.12);
        border-radius: 18px;
        padding: 16px 16px 14px 16px;
        box-shadow: 0 10px 28px rgba(11,45,92,0.08);
        position: relative;
        overflow: hidden;
        min-height: 92px;
    }
    .kpi-card:before {
        content: "";
        position: absolute;
        left: 0; top: 0;
        height: 100%;
        width: 7px;
        background: linear-gradient(180deg, #1E78FF 0%, #5AA9FF 100%);
        opacity: 0.95;
    }
    .kpi-label {
        font-size: 12.5px;
        font-weight: 700;
        color: rgba(11,45,92,0.75);
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-left: 10px;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 800;
        color: #0B2D5C;
        margin-left: 10px;
        margin-top: 6px;
        line-height: 1.1;
    }
    .kpi-sub {
        font-size: 12.5px;
        color: rgba(11,45,92,0.68);
        margin-left: 10px;
        margin-top: 6px;
    }

    /* Section card */
    .section-card {
        background: #FFFFFF;
        border: 1px solid rgba(11,45,92,0.10);
        border-radius: 18px;
        padding: 16px;
        box-shadow: 0 10px 28px rgba(11,45,92,0.06);
    }

    /* Tabs look */
    button[data-baseweb="tab"] {
        font-weight: 700 !important;
    }

    /* Small badge */
    .badge {
        display: inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        background: rgba(30,120,255,0.10);
        color: #0B2D5C;
        font-weight: 700;
        font-size: 12px;
        border: 1px solid rgba(30,120,255,0.18);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------
# DuckDB helpers
# ---------------------------
@st.cache_resource
def get_con():
    return duckdb.connect(DB_PATH, read_only=True)

def q(sql: str, params=None) -> pd.DataFrame:
    con = get_con()
    if params is None:
        return con.execute(sql).fetchdf()
    return con.execute(sql, params).fetchdf()

def money(x):
    """Simple wrapper around format_number for backward compatibility"""
    if x is None or pd.isna(x):
        return "—"
    return format_number(x, prefix="", suffix="").replace(",", " ")

# ---------------------------
# Sidebar header
# ---------------------------
st.sidebar.markdown("## 📊 Dashboard KPI")
st.sidebar.markdown("**Walmart Sales** & **Electric Vehicles**")
st.sidebar.markdown("---")

dataset = st.sidebar.selectbox("Dataset", ["walmart", "ev"], index=0)
st.sidebar.markdown("---")

# ---------------------------
# Main header
# ---------------------------
colA, colB = st.columns([0.72, 0.28], vertical_alignment="center")
with colA:
    st.markdown("# KPI Dashboard")
    st.markdown("Un tableau de bord interactif pour analyse & présentation.")
with colB:
    st.markdown('<span class="badge">Blue & White · Pro</span>', unsafe_allow_html=True)

# ---------------------------
# WALMART VIEW
# ---------------------------
if dataset == "walmart":
    # Filters
    stores = q("SELECT DISTINCT Store_Number FROM walmart ORDER BY Store_Number")["Store_Number"].tolist()
    store_sel = st.sidebar.multiselect("Store_Number", stores, default=stores)

    dmin = q("SELECT MIN(Date) AS dmin FROM walmart")["dmin"][0]
    dmax = q("SELECT MAX(Date) AS dmax FROM walmart")["dmax"][0]
    date_range = st.sidebar.date_input("Période (min, max)", value=(dmin, dmax))

    holiday_sel = st.sidebar.multiselect("Holiday_Flag", [0, 1], default=[0, 1])

    # Base WHERE reused
    # IMPORTANT: Weekly_Sales is VARCHAR => CAST + REPLACE
    where_params = [store_sel, holiday_sel, date_range[0], date_range[1]]

    # KPI: total, avg, max week, nb rows
    sql_kpis = """
    SELECT
      SUM(CAST(REPLACE(Weekly_Sales, ',', '') AS DOUBLE)) AS total_sales,
      AVG(CAST(REPLACE(Weekly_Sales, ',', '') AS DOUBLE)) AS avg_sales,
      MAX(CAST(REPLACE(Weekly_Sales, ',', '') AS DOUBLE)) AS max_sales,
      COUNT(*) AS nb_rows
    FROM walmart
    WHERE Store_Number IN (SELECT UNNEST(?))
      AND Holiday_Flag IN (SELECT UNNEST(?))
      AND Date BETWEEN ? AND ?;
    """
    k = q(sql_kpis, where_params).iloc[0]

    # Trend over time
    sql_time = """
    SELECT
      Date,
      SUM(CAST(REPLACE(Weekly_Sales, ',', '') AS DOUBLE)) AS total_sales
    FROM walmart
    WHERE Store_Number IN (SELECT UNNEST(?))
      AND Holiday_Flag IN (SELECT UNNEST(?))
      AND Date BETWEEN ? AND ?
    GROUP BY Date
    ORDER BY Date;
    """
    df_time = q(sql_time, where_params)

    # Store ranking
    sql_store = """
    SELECT
      Store_Number,
      SUM(CAST(REPLACE(Weekly_Sales, ',', '') AS DOUBLE)) AS total_sales
    FROM walmart
    WHERE Store_Number IN (SELECT UNNEST(?))
      AND Holiday_Flag IN (SELECT UNNEST(?))
      AND Date BETWEEN ? AND ?
    GROUP BY Store_Number
    ORDER BY total_sales DESC;
    """
    df_store = q(sql_store, where_params)

    # Holiday split
    sql_holiday = """
    SELECT
      Holiday_Flag,
      SUM(CAST(REPLACE(Weekly_Sales, ',', '') AS DOUBLE)) AS total_sales
    FROM walmart
    WHERE Store_Number IN (SELECT UNNEST(?))
      AND Holiday_Flag IN (SELECT UNNEST(?))
      AND Date BETWEEN ? AND ?
    GROUP BY Holiday_Flag
    ORDER BY Holiday_Flag;
    """
    df_holiday = q(sql_holiday, where_params)

    # KPI cards row
    st.markdown(
        f"""
        <div class="kpi-row">
            <div class="kpi-card">
                <div class="kpi-label">Total Ventes</div>
                <div class="kpi-value">{money(k["total_sales"])}</div>
                <div class="kpi-sub">Filtré (stores, dates, holiday)</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Moyenne / Semaine</div>
                <div class="kpi-value">{money(k["avg_sales"])}</div>
                <div class="kpi-sub">Vente hebdo moyenne</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Pic Hebdo</div>
                <div class="kpi-value">{money(k["max_sales"])}</div>
                <div class="kpi-sub">Valeur max observée</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Lignes</div>
                <div class="kpi-value">{int(k["nb_rows"])}</div>
                <div class="kpi-sub">Volume de données filtré</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Nouvelles requêtes pour visualisations avancées
    # 1. Performance hebdomadaire par store
    sql_weekly_perf = """
    SELECT
      Date,
      Store_Number,
      CAST(REPLACE(Weekly_Sales, ',', '') AS DOUBLE) AS sales
    FROM walmart
    WHERE Store_Number IN (SELECT UNNEST(?))
      AND Holiday_Flag IN (SELECT UNNEST(?))
      AND Date BETWEEN ? AND ?
    ORDER BY Date, Store_Number;
    """
    df_weekly_perf = q(sql_weekly_perf, where_params)

    # 2. Top et Bottom performers
    sql_performance = """
    SELECT
      Store_Number,
      SUM(CAST(REPLACE(Weekly_Sales, ',', '') AS DOUBLE)) AS total_sales,
      AVG(CAST(REPLACE(Weekly_Sales, ',', '') AS DOUBLE)) AS avg_sales,
      COUNT(*) AS nb_weeks
    FROM walmart
    WHERE Store_Number IN (SELECT UNNEST(?))
      AND Holiday_Flag IN (SELECT UNNEST(?))
      AND Date BETWEEN ? AND ?
    GROUP BY Store_Number
    ORDER BY total_sales DESC;
    """
    df_performance = q(sql_performance, where_params)

    # 3. Analyse Holiday Impact
    sql_holiday_impact = """
    SELECT
      Store_Number,
      Holiday_Flag,
      AVG(CAST(REPLACE(Weekly_Sales, ',', '') AS DOUBLE)) AS avg_sales
    FROM walmart
    WHERE Store_Number IN (SELECT UNNEST(?))
      AND Holiday_Flag IN (SELECT UNNEST(?))
      AND Date BETWEEN ? AND ?
    GROUP BY Store_Number, Holiday_Flag
    ORDER BY Store_Number, Holiday_Flag;
    """
    df_holiday_impact = q(sql_holiday_impact, where_params)

    # 4. Distribution temporelle
    sql_distribution = """
    SELECT
      CAST(REPLACE(Weekly_Sales, ',', '') AS DOUBLE) AS sales,
      Holiday_Flag,
      Store_Number
    FROM walmart
    WHERE Store_Number IN (SELECT UNNEST(?))
      AND Holiday_Flag IN (SELECT UNNEST(?))
      AND Date BETWEEN ? AND ?;
    """
    df_distribution = q(sql_distribution, where_params)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Vue KPI", "🏬 Comparaison Stores", "📊 Analyses Avancées", "🔬 Comparateur", "🧾 Détails"])

    with tab1:
        c1, c2 = st.columns([0.65, 0.35], gap="large")

        with c1:
            with section_card():
                st.markdown("### Évolution des ventes")
                fig = px.line(df_time, x="Date", y="total_sales", markers=True)
                fig.update_layout(
                    height=420,
                    margin=dict(l=10, r=10, t=50, b=10),
                    title=None,
                    xaxis_title=None,
                    yaxis_title="Total ventes",
                )
                fig.update_traces(line_color='#1E78FF', marker=dict(size=6))
                st.plotly_chart(fig, use_container_width=True)

        with c2:
            with section_card():
                st.markdown("### Holiday vs Non-Holiday")
                # Make labels nicer
                df_holiday2 = df_holiday.copy()
                df_holiday2["Holiday"] = df_holiday2["Holiday_Flag"].map({0: "Non-Holiday", 1: "Holiday"})
                fig2 = px.pie(df_holiday2, names="Holiday", values="total_sales", hole=0.45,
                             color_discrete_sequence=['#1E78FF', '#5AA9FF'])
                fig2.update_layout(height=420, margin=dict(l=10, r=10, t=50, b=10))
                st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        with section_card():
            st.markdown("### Classement des stores (ventes totales)")
            fig3 = px.bar(df_store.head(15), x="Store_Number", y="total_sales",
                         color="total_sales", color_continuous_scale="Blues")
            fig3.update_layout(height=420, margin=dict(l=10, r=10, t=50, b=10), 
                              xaxis_title="Store", yaxis_title="Total ventes")
            st.plotly_chart(fig3, use_container_width=True)

    with tab3:
        st.markdown("### 📊 Analyses Avancées")
        
        # Ligne 1: Top/Bottom Performers et Holiday Impact
        col1, col2 = st.columns(2, gap="large")
        
        with col1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("#### 🏆 Performance des Stores (Interactif)")
            
            # Widget pour choisir combien de top/bottom stores afficher
            n_stores = st.slider("Nombre de stores à afficher (Top & Bottom)", 
                               min_value=3, max_value=15, value=10, key="n_stores_perf")
            
            # Préparer top et bottom
            top_n = df_performance.head(n_stores).copy()
            top_n['Category'] = f'Top {n_stores}'
            bottom_n = df_performance.tail(n_stores).copy()
            bottom_n['Category'] = f'Bottom {n_stores}'
            
            df_top_bottom = pd.concat([top_n, bottom_n])
            
            fig_perf = px.bar(df_top_bottom, 
                             x="Store_Number", 
                             y="total_sales",
                             color="Category",
                             color_discrete_map={f'Top {n_stores}': '#1E78FF', f'Bottom {n_stores}': '#FF6B6B'},
                             barmode='group')
            
            fig_perf.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10))
            fig_perf.update_xaxes(title_text="Store Number")
            fig_perf.update_yaxes(title_text="Total Ventes ($)")
            
            st.plotly_chart(fig_perf, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("#### 🎉 Impact des Jours Fériés par Store")
            
            # Widget pour trier
            sort_option = st.radio(
                "Trier par",
                ["Impact le plus fort", "Impact le plus faible"],
                horizontal=True,
                key="holiday_sort"
            )
            
            # Pivot pour comparer
            df_pivot = df_holiday_impact.pivot(index="Store_Number", columns="Holiday_Flag", values="avg_sales")
            if 0 in df_pivot.columns and 1 in df_pivot.columns:
                df_pivot['Impact'] = ((df_pivot[1] - df_pivot[0]) / df_pivot[0] * 100).round(1)
                
                if sort_option == "Impact le plus fort":
                    df_pivot = df_pivot.sort_values('Impact', ascending=False).head(10)
                else:
                    df_pivot = df_pivot.sort_values('Impact', ascending=True).head(10)
                
                fig_impact = px.bar(df_pivot.reset_index(), 
                                   x="Store_Number", 
                                   y="Impact",
                                   color="Impact",
                                   color_continuous_scale=["#FF6B6B", "#FFEB3B", "#4ECDC4"])
                
                fig_impact.update_layout(height=250, margin=dict(l=10, r=10, t=10, b=10))
                fig_impact.update_xaxes(title_text="Store Number")
                fig_impact.update_yaxes(title_text="Impact Holiday (%)")
                
                st.plotly_chart(fig_impact, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Ligne 2: Distribution et Tendance comparative
        col3, col4 = st.columns(2, gap="large")
        
        with col3:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("#### � Catégories de Performance des Stores")
            
            st.caption("💡 **Classification**: Les stores sont classés en 3 catégories selon leurs ventes totales")
            
            # Utiliser la fonction utils pour classifier
            df_performance, q33, q66 = categorize_performance(df_performance, 'total_sales', categories=3)
            
            # Sélecteur pour voir soit le résumé, soit les détails
            view_mode = st.radio(
                "Vue",
                ["📊 Résumé", "🏬 Détails par Store"],
                horizontal=True,
                key="perf_category_view"
            )
            
            if view_mode == "📊 Résumé":
                # Compter les stores par catégorie
                category_counts = df_performance['Catégorie'].value_counts().reset_index()
                category_counts.columns = ['Catégorie', 'Nombre de Stores']
                
                # Graphique en barres avec couleurs
                fig_cat = create_bar_chart(
                    category_counts,
                    x='Catégorie',
                    y='Nombre de Stores',
                    color='Catégorie',
                    color_map={
                        '⚠️ Faible': '#FF6B6B',
                        '✅ Moyen': '#FFD93D',
                        '🌟 Élevé': '#4ECDC4'
                    },
                    title_x="Niveau de Performance",
                    title_y="Nombre de Stores",
                    height=200
                )
                fig_cat.update_layout(showlegend=False)
                st.plotly_chart(fig_cat, use_container_width=True)
            
            else:
                # Afficher tous les stores avec leur catégorie
                df_display = df_performance[['Store_Number', 'total_sales', 'Catégorie']].copy()
                df_display = df_display.sort_values('total_sales', ascending=False)
                
                # Graphique avec tous les stores colorés par catégorie
                fig_stores = px.bar(
                    df_display,
                    x='Store_Number',
                    y='total_sales',
                    color='Catégorie',
                    color_discrete_map={
                        '⚠️ Faible': '#FF6B6B',
                        '✅ Moyen': '#FFD93D',
                        '🌟 Élevé': '#4ECDC4'
                    },
                    hover_data=['total_sales']
                )
                fig_stores.update_layout(
                    height=200,
                    margin=dict(l=10, r=10, t=10, b=10),
                    xaxis_title="Store Number",
                    yaxis_title="Ventes Totales ($)"
                )
                st.plotly_chart(fig_stores, use_container_width=True)
            
            # Statistiques simples
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                faible = len(df_performance[df_performance['Catégorie'] == '⚠️ Faible'])
                st.metric("⚠️ Faible", faible, help=f"< ${q33:,.0f}")
            with col_b:
                moyen = len(df_performance[df_performance['Catégorie'] == '✅ Moyen'])
                st.metric("✅ Moyen", moyen, help=f"${q33:,.0f} - ${q66:,.0f}")
            with col_c:
                eleve = len(df_performance[df_performance['Catégorie'] == '🌟 Élevé'])
                st.metric("🌟 Élevé", eleve, help=f"> ${q66:,.0f}")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("#### 📈 Comparaison de Stores (Interactif)")
            
            # Widget pour choisir les stores à comparer
            all_stores = df_performance['Store_Number'].tolist()
            top_5_default = df_performance.head(5)['Store_Number'].tolist()
            
            selected_stores = st.multiselect(
                "Sélectionnez les stores à comparer",
                options=all_stores,
                default=top_5_default,
                key="store_comparison"
            )
            
            if selected_stores:
                df_selected_trend = df_weekly_perf[df_weekly_perf['Store_Number'].isin(selected_stores)]
                
                fig_trend = px.line(df_selected_trend, 
                                   x="Date", 
                                   y="sales",
                                   color="Store_Number",
                                   color_discrete_sequence=px.colors.sequential.Blues_r)
                
                fig_trend.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10))
                fig_trend.update_xaxes(title_text="Date")
                fig_trend.update_yaxes(title_text="Ventes ($)")
                
                st.plotly_chart(fig_trend, use_container_width=True)
            else:
                st.info("👆 Sélectionnez au moins un store pour voir la tendance")
            
            st.markdown("</div>", unsafe_allow_html=True)

    with tab4:
        st.markdown("### 🔬 Comparateur de Caractéristiques (Personnalisable)")
        
        st.info("💡 Créez vos propres graphiques en choisissant les axes X et Y pour chaque visualisation!")
        
        # Requête pour obtenir toutes les données avec moyennes par store
        sql_all_walmart = """
        SELECT 
            Store_Number,
            AVG(CAST(REPLACE(Weekly_Sales, ',', '') AS DOUBLE)) as avg_weekly_sales,
            AVG(Temperature) as avg_temperature,
            AVG(Fuel_Price) as avg_fuel_price,
            AVG(CPI) as avg_cpi,
            AVG(Unemployment) as avg_unemployment,
            SUM(CASE WHEN Holiday_Flag = 1 THEN CAST(REPLACE(Weekly_Sales, ',', '') AS DOUBLE) ELSE 0 END) as holiday_sales,
            SUM(CASE WHEN Holiday_Flag = 0 THEN CAST(REPLACE(Weekly_Sales, ',', '') AS DOUBLE) ELSE 0 END) as regular_sales,
            COUNT(*) as num_records,
            COUNT(CASE WHEN Holiday_Flag = 1 THEN 1 END) as num_holidays
        FROM walmart
        WHERE Store_Number IN (SELECT UNNEST(?))
          AND Holiday_Flag IN (SELECT UNNEST(?))
          AND Date BETWEEN ? AND ?
        GROUP BY Store_Number;
        """
        df_all_walmart = q(sql_all_walmart, where_params)
        
        # Calculer des métriques dérivées
        df_all_walmart['total_sales'] = df_all_walmart['holiday_sales'] + df_all_walmart['regular_sales']
        df_all_walmart['holiday_impact_pct'] = ((df_all_walmart['holiday_sales'] / df_all_walmart['num_holidays']) / 
                                                 (df_all_walmart['regular_sales'] / (df_all_walmart['num_records'] - df_all_walmart['num_holidays'])) * 100 - 100).round(1)
        
        # Liste des caractéristiques numériques disponibles
        numeric_features_walmart = {
            'avg_weekly_sales': 'Ventes Moyennes ($)',
            'total_sales': 'Ventes Totales ($)',
            'avg_temperature': 'Température Moyenne (°F)',
            'avg_fuel_price': 'Prix Carburant Moyen ($)',
            'avg_cpi': 'CPI Moyen',
            'avg_unemployment': 'Taux Chômage Moyen (%)',
            'holiday_sales': 'Ventes en Jours Fériés ($)',
            'regular_sales': 'Ventes Jours Normaux ($)',
            'holiday_impact_pct': 'Impact Holiday (%)',
            'num_records': 'Nombre de Semaines',
            'num_holidays': 'Nombre de Jours Fériés'
        }
        
        # Grille 2x2 de graphiques personnalisables
        st.markdown("---")
        
        # Ligne 1
        col1, col2 = st.columns(2, gap="large")
        
        with col1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("#### 📊 Graphique 1")
            
            col_x1, col_y1 = st.columns(2)
            with col_x1:
                x_axis_w1 = st.selectbox("Axe X", list(numeric_features_walmart.keys()), 
                                       format_func=lambda x: numeric_features_walmart[x],
                                       key="xw1", index=0)  # avg_weekly_sales
            with col_y1:
                y_axis_w1 = st.selectbox("Axe Y", list(numeric_features_walmart.keys()),
                                       format_func=lambda x: numeric_features_walmart[x],
                                       key="yw1", index=8)  # holiday_impact_pct
            
            # Filtrer les données avec valeurs non nulles
            df_plot_w1 = df_all_walmart.dropna(subset=[x_axis_w1, y_axis_w1])
            
            if len(df_plot_w1) > 0:
                fig_w1 = px.scatter(df_plot_w1, x=x_axis_w1, y=y_axis_w1,
                                   hover_data=["Store_Number"],
                                   color="Store_Number",
                                   color_continuous_scale="Blues")
                fig_w1.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
                fig_w1.update_xaxes(title_text=numeric_features_walmart[x_axis_w1])
                fig_w1.update_yaxes(title_text=numeric_features_walmart[y_axis_w1])
                st.plotly_chart(fig_w1, use_container_width=True)
            else:
                st.warning("Pas assez de données pour ces axes")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("#### 📊 Graphique 2")
            
            col_x2, col_y2 = st.columns(2)
            with col_x2:
                x_axis_w2 = st.selectbox("Axe X", list(numeric_features_walmart.keys()),
                                       format_func=lambda x: numeric_features_walmart[x],
                                       key="xw2", index=5)  # avg_unemployment
            with col_y2:
                y_axis_w2 = st.selectbox("Axe Y", list(numeric_features_walmart.keys()),
                                       format_func=lambda x: numeric_features_walmart[x],
                                       key="yw2", index=0)  # avg_weekly_sales
            
            df_plot_w2 = df_all_walmart.dropna(subset=[x_axis_w2, y_axis_w2])
            
            if len(df_plot_w2) > 0:
                fig_w2 = px.scatter(df_plot_w2, x=x_axis_w2, y=y_axis_w2,
                                   hover_data=["Store_Number"],
                                   color="Store_Number",
                                   color_continuous_scale="Teal")
                fig_w2.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
                fig_w2.update_xaxes(title_text=numeric_features_walmart[x_axis_w2])
                fig_w2.update_yaxes(title_text=numeric_features_walmart[y_axis_w2])
                st.plotly_chart(fig_w2, use_container_width=True)
            else:
                st.warning("Pas assez de données pour ces axes")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Ligne 2
        col3, col4 = st.columns(2, gap="large")
        
        with col3:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("#### 📊 Graphique 3")
            
            col_x3, col_y3 = st.columns(2)
            with col_x3:
                x_axis_w3 = st.selectbox("Axe X", list(numeric_features_walmart.keys()),
                                       format_func=lambda x: numeric_features_walmart[x],
                                       key="xw3", index=3)  # avg_fuel_price
            with col_y3:
                y_axis_w3 = st.selectbox("Axe Y", list(numeric_features_walmart.keys()),
                                       format_func=lambda x: numeric_features_walmart[x],
                                       key="yw3", index=1)  # total_sales
            
            df_plot_w3 = df_all_walmart.dropna(subset=[x_axis_w3, y_axis_w3])
            
            if len(df_plot_w3) > 0:
                fig_w3 = px.scatter(df_plot_w3, x=x_axis_w3, y=y_axis_w3,
                                   hover_data=["Store_Number"],
                                   color="Store_Number",
                                   color_continuous_scale="Sunset")
                fig_w3.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
                fig_w3.update_xaxes(title_text=numeric_features_walmart[x_axis_w3])
                fig_w3.update_yaxes(title_text=numeric_features_walmart[y_axis_w3])
                st.plotly_chart(fig_w3, use_container_width=True)
            else:
                st.warning("Pas assez de données pour ces axes")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("#### 📊 Graphique 4")
            
            col_x4, col_y4 = st.columns(2)
            with col_x4:
                x_axis_w4 = st.selectbox("Axe X", list(numeric_features_walmart.keys()),
                                       format_func=lambda x: numeric_features_walmart[x],
                                       key="xw4", index=4)  # avg_cpi
            with col_y4:
                y_axis_w4 = st.selectbox("Axe Y", list(numeric_features_walmart.keys()),
                                       format_func=lambda x: numeric_features_walmart[x],
                                       key="yw4", index=0)  # avg_weekly_sales
            
            df_plot_w4 = df_all_walmart.dropna(subset=[x_axis_w4, y_axis_w4])
            
            if len(df_plot_w4) > 0:
                fig_w4 = px.scatter(df_plot_w4, x=x_axis_w4, y=y_axis_w4,
                                   hover_data=["Store_Number"],
                                   color="Store_Number",
                                   color_continuous_scale="Purp")
                fig_w4.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
                fig_w4.update_xaxes(title_text=numeric_features_walmart[x_axis_w4])
                fig_w4.update_yaxes(title_text=numeric_features_walmart[y_axis_w4])
                st.plotly_chart(fig_w4, use_container_width=True)
            else:
                st.warning("Pas assez de données pour ces axes")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Suggestions de comparaisons intéressantes
        st.markdown("---")
        st.markdown("### 💡 Suggestions de Comparaisons Intéressantes:")
        
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            st.info("**💰 Performance**\n- Ventes vs Impact Holiday\n- Ventes vs Nombre Semaines")
        with col_s2:
            st.info("**📊 Économie**\n- Chômage vs Ventes\n- CPI vs Ventes\n- Prix Carburant vs Ventes")
        with col_s3:
            st.info("**🎯 Stratégie**\n- Jours Fériés vs Impact\n- Ventes Holiday vs Regular")

    with tab5:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### Aperçu des données (50 lignes)")
        sql_preview = """
        SELECT Store_Number, Date, Weekly_Sales, Holiday_Flag, Temperature, Fuel_Price, CPI, Unemployment
        FROM walmart
        WHERE Store_Number IN (SELECT UNNEST(?))
          AND Holiday_Flag IN (SELECT UNNEST(?))
          AND Date BETWEEN ? AND ?
        LIMIT 50;
        """
        st.dataframe(q(sql_preview, where_params), use_container_width=True, height=420)
        st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# EV VIEW
# ---------------------------
else:
    brands = q("SELECT DISTINCT brand FROM ev WHERE brand IS NOT NULL ORDER BY brand")["brand"].tolist()
    brand_sel = st.sidebar.multiselect("brand", brands, default=brands[:6] if len(brands) >= 6 else brands)

    segments = q("SELECT DISTINCT segment FROM ev WHERE segment IS NOT NULL ORDER BY segment")["segment"].tolist()
    segment_sel = st.sidebar.multiselect("segment", segments, default=segments)

    # KPI cards
    sql_ev_kpi = """
    SELECT
      COUNT(*) AS nb_models,
      AVG(range_km) AS avg_range,
      AVG(battery_capacity_kWh) AS avg_batt,
      AVG(top_speed_kmh) AS avg_speed
    FROM ev
    WHERE brand IN (SELECT UNNEST(?))
      AND segment IN (SELECT UNNEST(?));
    """
    ek = q(sql_ev_kpi, [brand_sel, segment_sel]).iloc[0]

    st.markdown(
        f"""
        <div class="kpi-row">
            <div class="kpi-card">
                <div class="kpi-label">Modèles</div>
                <div class="kpi-value">{int(ek["nb_models"])}</div>
                <div class="kpi-sub">Dans la sélection</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Autonomie Moy.</div>
                <div class="kpi-value">{money(ek["avg_range"]) } km</div>
                <div class="kpi-sub">range_km</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Batterie Moy.</div>
                <div class="kpi-value">{money(ek["avg_batt"]) } kWh</div>
                <div class="kpi-sub">battery_capacity_kWh</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Vitesse Moy.</div>
                <div class="kpi-value">{money(ek["avg_speed"]) } km/h</div>
                <div class="kpi-sub">top_speed_kmh</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🚗 Top Autonomie", "🏷️ Marques", "📊 Analyses Avancées", "🔬 Comparateur", "🧾 Détails"])

    with tab1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 🚗 Top Autonomies (Interactif)")
        
        col_x, col_y = st.columns([0.7, 0.3])
        
        with col_x:
            # Slider pour choisir combien de modèles afficher
            n_top = st.slider("Nombre de modèles à afficher", 
                            min_value=5, max_value=20, value=10, key="n_top_ev")
        
        with col_y:
            # Filtre par segment spécifique
            view_segment = st.selectbox(
                "Segment",
                ["Tous"] + segment_sel,
                key="segment_filter_top"
            )
        
        sql_top = """
        SELECT brand, model, range_km, segment
        FROM ev
        WHERE brand IN (SELECT UNNEST(?))
          AND segment IN (SELECT UNNEST(?))
          AND range_km IS NOT NULL
        ORDER BY range_km DESC
        LIMIT ?;
        """
        df_top_all = q(sql_top, [brand_sel, segment_sel, n_top])
        
        # Filtrer par segment si sélectionné
        if view_segment != "Tous":
            df_top = df_top_all[df_top_all['segment'] == view_segment].head(n_top)
        else:
            df_top = df_top_all
        
        if len(df_top) > 0:
            fig = px.bar(df_top, x="model", y="range_km", 
                        hover_data=["brand", "segment"],
                        color="brand",
                        color_discrete_sequence=px.colors.qualitative.Set2)
            fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10), 
                            xaxis_title="Modèle", yaxis_title="Autonomie (km)")
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
            
            # Champion
            champion = df_top.iloc[0]
            st.success(f"🏆 Champion: **{champion['brand']} {champion['model']}** - {champion['range_km']:.0f} km")
        else:
            st.warning("Aucun modèle trouvé avec ces critères")
        
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 🏷️ Autonomie par Marque (Interactif)")
        
        # Obtenir toutes les marques disponibles
        sql_all_brands = """
        SELECT brand, AVG(range_km) AS avg_range_km, COUNT(*) as nb_models
        FROM ev
        WHERE brand IN (SELECT UNNEST(?))
          AND segment IN (SELECT UNNEST(?))
          AND range_km IS NOT NULL
        GROUP BY brand
        ORDER BY avg_range_km DESC;
        """
        df_all_brands = q(sql_all_brands, [brand_sel, segment_sel])
        
        col_a, col_b = st.columns([0.7, 0.3])
        
        with col_a:
            # Widget pour sélectionner les marques à afficher
            all_available_brands = df_all_brands['brand'].tolist()
            top_5_brands = df_all_brands.head(5)['brand'].tolist()
            
            selected_brands = st.multiselect(
                "Sélectionnez les marques à comparer",
                options=all_available_brands,
                default=top_5_brands,
                key="brand_comparison"
            )
        
        with col_b:
            # Option de tri
            sort_by = st.radio(
                "Trier par",
                ["Autonomie", "Nombre de modèles"],
                key="brand_sort"
            )
        
        if selected_brands:
            df_filtered_brands = df_all_brands[df_all_brands['brand'].isin(selected_brands)].copy()
            
            if sort_by == "Autonomie":
                df_filtered_brands = df_filtered_brands.sort_values('avg_range_km', ascending=False)
                y_col = 'avg_range_km'
                y_title = 'Autonomie moyenne (km)'
            else:
                df_filtered_brands = df_filtered_brands.sort_values('nb_models', ascending=False)
                y_col = 'nb_models'
                y_title = 'Nombre de modèles'
            
            fig2 = px.bar(df_filtered_brands, x="brand", y=y_col,
                         color=y_col, color_continuous_scale="Blues",
                         hover_data=['avg_range_km', 'nb_models'])
            fig2.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10), 
                             xaxis_title="Marque", yaxis_title=y_title)
            st.plotly_chart(fig2, use_container_width=True)
            
            # Statistiques
            col1, col2, col3 = st.columns(3)
            with col1:
                best_brand = df_filtered_brands.nlargest(1, 'avg_range_km').iloc[0]
                st.metric("🏆 Meilleure Autonomie", best_brand['brand'], 
                         f"{best_brand['avg_range_km']:.0f} km")
            with col2:
                most_models = df_filtered_brands.nlargest(1, 'nb_models').iloc[0]
                st.metric("📊 Plus de Modèles", most_models['brand'], 
                         f"{int(most_models['nb_models'])} modèles")
            with col3:
                avg_all = df_filtered_brands['avg_range_km'].mean()
                st.metric("📈 Moyenne Générale", f"{avg_all:.0f} km")
        else:
            st.info("👆 Sélectionnez au moins une marque pour voir la comparaison")
        
        st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.markdown("### 📊 Visualisations Avancées")
        
        # Nouvelles requêtes pour EV
        sql_scatter = """
        SELECT brand, model, range_km, battery_capacity_kWh, top_speed_kmh, segment
        FROM ev
        WHERE brand IN (SELECT UNNEST(?))
          AND segment IN (SELECT UNNEST(?))
          AND range_km IS NOT NULL
          AND battery_capacity_kWh IS NOT NULL;
        """
        df_scatter = q(sql_scatter, [brand_sel, segment_sel])
        
        sql_segment = """
        SELECT 
            segment,
            COUNT(*) as nb_models,
            AVG(range_km) as avg_range,
            AVG(battery_capacity_kWh) as avg_battery
        FROM ev
        WHERE brand IN (SELECT UNNEST(?))
          AND segment IN (SELECT UNNEST(?))
          AND segment IS NOT NULL
        GROUP BY segment
        ORDER BY nb_models DESC;
        """
        df_segment = q(sql_segment, [brand_sel, segment_sel])
        
        sql_speed_dist = """
        SELECT top_speed_kmh, brand, segment
        FROM ev
        WHERE brand IN (SELECT UNNEST(?))
          AND segment IN (SELECT UNNEST(?))
          AND top_speed_kmh IS NOT NULL;
        """
        df_speed = q(sql_speed_dist, [brand_sel, segment_sel])
        
        # Ligne 1: Scatter et Segment comparison
        col1, col2 = st.columns(2, gap="large")
        
        with col1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("#### ⚡ Autonomie vs Capacité Batterie (Interactif)")
            
            # Options de coloration
            color_by = st.radio(
                "Colorer par",
                ["Segment", "Marque"],
                horizontal=True,
                key="scatter_color"
            )
            
            # Options de taille
            size_by = st.selectbox(
                "Taille des bulles selon",
                ["Vitesse Max", "Autonomie"],
                key="scatter_size"
            )
            
            color_col = "segment" if color_by == "Segment" else "brand"
            size_col = "top_speed_kmh" if size_by == "Vitesse Max" else "range_km"
            
            fig_scatter = px.scatter(df_scatter, 
                                    x="battery_capacity_kWh", 
                                    y="range_km",
                                    color=color_col,
                                    size=size_col,
                                    hover_data=["brand", "model", "segment"],
                                    color_discrete_sequence=px.colors.qualitative.Set2 if color_by == "Segment" else px.colors.qualitative.Plotly)
            
            fig_scatter.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10))
            fig_scatter.update_xaxes(title_text="Capacité Batterie (kWh)")
            fig_scatter.update_yaxes(title_text="Autonomie (km)")
            
            st.plotly_chart(fig_scatter, use_container_width=True)
            st.caption("💡 Plus grande batterie = plus d'autonomie (corrélation positive)")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("#### 🚙 Comparaison par Segment")
            
            fig_segment = go.Figure()
            
            fig_segment.add_trace(go.Bar(
                name='Nb Modèles',
                x=df_segment['segment'],
                y=df_segment['nb_models'],
                marker_color='#1E78FF'
            ))
            
            fig_segment.add_trace(go.Bar(
                name='Autonomie Moy',
                x=df_segment['segment'],
                y=df_segment['avg_range'] / 10,  # Scale pour visibilité
                marker_color='#5AA9FF'
            ))
            
            fig_segment.update_layout(
                barmode='group',
                height=350,
                margin=dict(l=10, r=10, t=30, b=10),
                yaxis_title="Valeur"
            )
            
            st.plotly_chart(fig_segment, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Ligne 2: Distribution vitesse et Bubble chart
        col3, col4 = st.columns(2, gap="large")
        
        with col3:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("#### 🏁 Distribution des Vitesses Max")
            
            # Options de visualisation
            col_opt1, col_opt2 = st.columns(2)
            
            with col_opt1:
                view_mode = st.radio(
                    "Vue",
                    ["Histogram", "Box Plot"],
                    horizontal=True,
                    key="speed_view"
                )
            
            with col_opt2:
                if view_mode == "Histogram":
                    n_bins_speed = st.slider("Bins", 10, 50, 30, key="speed_bins")
            
            if view_mode == "Histogram":
                fig_speed = px.histogram(df_speed, 
                                        x="top_speed_kmh",
                                        nbins=n_bins_speed,
                                        color_discrete_sequence=['#1E78FF'])
                
                fig_speed.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10))
                fig_speed.update_xaxes(title_text="Vitesse Max (km/h)")
                fig_speed.update_yaxes(title_text="Nombre de modèles")
            else:
                # Box plot par segment
                fig_speed = px.box(df_speed,
                                  x="segment",
                                  y="top_speed_kmh",
                                  color="segment",
                                  color_discrete_sequence=px.colors.qualitative.Set2)
                
                fig_speed.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10),
                                      showlegend=False)
                fig_speed.update_xaxes(title_text="Segment")
                fig_speed.update_yaxes(title_text="Vitesse Max (km/h)")
            
            st.plotly_chart(fig_speed, use_container_width=True)
            
            # Statistiques
            avg_speed = df_speed['top_speed_kmh'].mean()
            max_speed = df_speed['top_speed_kmh'].max()
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                st.metric("Moyenne", f"{avg_speed:.0f} km/h")
            with col_s2:
                st.metric("Maximum", f"{max_speed:.0f} km/h")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("#### 🎯 Bubble Chart Multi-Dimensions (Interactif)")
            
            # Obtenir toutes les marques disponibles dans df_scatter
            available_brands = sorted(df_scatter['brand'].unique().tolist())
            
            # Widget pour choisir les marques
            selected_bubble_brands = st.multiselect(
                "Choisir les marques à afficher",
                options=available_brands,
                default=available_brands[:5] if len(available_brands) >= 5 else available_brands,
                key="bubble_brands"
            )
            
            # Slider pour nombre de modèles
            n_models = st.slider(
                "Nombre de modèles (top autonomie)",
                min_value=5, max_value=50, value=20,
                key="bubble_n_models"
            )
            
            if selected_bubble_brands:
                # Filtrer par marques sélectionnées
                df_bubble_filtered = df_scatter[df_scatter['brand'].isin(selected_bubble_brands)]
                df_bubble = df_bubble_filtered.nlargest(n_models, 'range_km')
                
                if len(df_bubble) > 0:
                    fig_bubble = px.scatter(df_bubble,
                                           x="battery_capacity_kWh",
                                           y="top_speed_kmh",
                                           size="range_km",
                                           color="brand",
                                           hover_name="model",
                                           hover_data={
                                               'range_km': ':.0f',
                                               'battery_capacity_kWh': ':.1f',
                                               'top_speed_kmh': ':.0f',
                                               'segment': True
                                           },
                                           size_max=60)
                    
                    fig_bubble.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10))
                    fig_bubble.update_xaxes(title_text="Batterie (kWh)")
                    fig_bubble.update_yaxes(title_text="Vitesse Max (km/h)")
                    
                    st.plotly_chart(fig_bubble, use_container_width=True)
                    
                    # Légende explicative
                    st.caption("💡 **Taille de bulle** = Autonomie (km) | **Couleur** = Marque")
                else:
                    st.warning("Aucun modèle trouvé pour ces marques")
            else:
                st.info("👆 Sélectionnez au moins une marque pour voir le bubble chart")
            
            st.markdown("</div>", unsafe_allow_html=True)

    with tab4:
        st.markdown("### 🔬 Comparateur de Caractéristiques (Personnalisable)")
        
        st.info("💡 Créez vos propres graphiques en choisissant les axes X et Y pour chaque visualisation!")
        
        # Requête pour obtenir toutes les données
        sql_all_features = """
        SELECT 
            brand, model, top_speed_kmh, battery_capacity_kWh, 
            torque_nm, efficiency_wh_per_km, range_km, acceleration_0_100_s,
            fast_charging_power_kw_dc, towing_capacity_kg, cargo_volume_l, 
            seats, segment, length_mm, width_mm, height_mm
        FROM ev
        WHERE brand IN (SELECT UNNEST(?))
          AND segment IN (SELECT UNNEST(?));
        """
        df_all_features = q(sql_all_features, [brand_sel, segment_sel])
        
        # Liste des caractéristiques numériques disponibles
        numeric_features = {
            'top_speed_kmh': 'Vitesse Max (km/h)',
            'battery_capacity_kWh': 'Capacité Batterie (kWh)',
            'torque_nm': 'Couple (Nm)',
            'efficiency_wh_per_km': 'Efficacité (Wh/km)',
            'range_km': 'Autonomie (km)',
            'acceleration_0_100_s': 'Accélération 0-100 (s)',
            'fast_charging_power_kw_dc': 'Charge Rapide (kW)',
            'towing_capacity_kg': 'Capacité Remorquage (kg)',
            'cargo_volume_l': 'Volume Cargo (L)',
            'seats': 'Nombre de Sièges',
            'length_mm': 'Longueur (mm)',
            'width_mm': 'Largeur (mm)',
            'height_mm': 'Hauteur (mm)'
        }
        
        # Grille 2x2 de graphiques personnalisables
        st.markdown("---")
        
        # Ligne 1
        col1, col2 = st.columns(2, gap="large")
        
        with col1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("#### 📊 Graphique 1")
            
            col_x1, col_y1, col_c1 = st.columns(3)
            with col_x1:
                x_axis_1 = st.selectbox("Axe X", list(numeric_features.keys()), 
                                       format_func=lambda x: numeric_features[x],
                                       key="x1", index=1)  # battery_capacity_kWh
            with col_y1:
                y_axis_1 = st.selectbox("Axe Y", list(numeric_features.keys()),
                                       format_func=lambda x: numeric_features[x],
                                       key="y1", index=4)  # range_km
            with col_c1:
                color_1 = st.selectbox("Couleur", ["segment", "brand"], key="c1")
            
            # Filtrer les données avec valeurs non nulles
            df_plot1 = df_all_features.dropna(subset=[x_axis_1, y_axis_1])
            
            if len(df_plot1) > 0:
                fig1 = px.scatter(df_plot1, x=x_axis_1, y=y_axis_1, color=color_1,
                                 hover_data=["brand", "model"],
                                 color_discrete_sequence=px.colors.qualitative.Set2)
                fig1.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
                fig1.update_xaxes(title_text=numeric_features[x_axis_1])
                fig1.update_yaxes(title_text=numeric_features[y_axis_1])
                st.plotly_chart(fig1, use_container_width=True)
            else:
                st.warning("Pas assez de données pour ces axes")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("#### 📊 Graphique 2")
            
            col_x2, col_y2, col_c2 = st.columns(3)
            with col_x2:
                x_axis_2 = st.selectbox("Axe X", list(numeric_features.keys()),
                                       format_func=lambda x: numeric_features[x],
                                       key="x2", index=0)  # top_speed_kmh
            with col_y2:
                y_axis_2 = st.selectbox("Axe Y", list(numeric_features.keys()),
                                       format_func=lambda x: numeric_features[x],
                                       key="y2", index=5)  # acceleration_0_100_s
            with col_c2:
                color_2 = st.selectbox("Couleur", ["segment", "brand"], key="c2")
            
            df_plot2 = df_all_features.dropna(subset=[x_axis_2, y_axis_2])
            
            if len(df_plot2) > 0:
                fig2 = px.scatter(df_plot2, x=x_axis_2, y=y_axis_2, color=color_2,
                                 hover_data=["brand", "model"],
                                 color_discrete_sequence=px.colors.qualitative.Plotly)
                fig2.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
                fig2.update_xaxes(title_text=numeric_features[x_axis_2])
                fig2.update_yaxes(title_text=numeric_features[y_axis_2])
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.warning("Pas assez de données pour ces axes")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Ligne 2
        col3, col4 = st.columns(2, gap="large")
        
        with col3:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("#### 📊 Graphique 3")
            
            col_x3, col_y3, col_c3 = st.columns(3)
            with col_x3:
                x_axis_3 = st.selectbox("Axe X", list(numeric_features.keys()),
                                       format_func=lambda x: numeric_features[x],
                                       key="x3", index=2)  # torque_nm
            with col_y3:
                y_axis_3 = st.selectbox("Axe Y", list(numeric_features.keys()),
                                       format_func=lambda x: numeric_features[x],
                                       key="y3", index=0)  # top_speed_kmh
            with col_c3:
                color_3 = st.selectbox("Couleur", ["segment", "brand"], key="c3")
            
            df_plot3 = df_all_features.dropna(subset=[x_axis_3, y_axis_3])
            
            if len(df_plot3) > 0:
                fig3 = px.scatter(df_plot3, x=x_axis_3, y=y_axis_3, color=color_3,
                                 hover_data=["brand", "model"],
                                 color_discrete_sequence=px.colors.qualitative.Safe)
                fig3.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
                fig3.update_xaxes(title_text=numeric_features[x_axis_3])
                fig3.update_yaxes(title_text=numeric_features[y_axis_3])
                st.plotly_chart(fig3, use_container_width=True)
            else:
                st.warning("Pas assez de données pour ces axes")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("#### 📊 Graphique 4")
            
            col_x4, col_y4, col_c4 = st.columns(3)
            with col_x4:
                x_axis_4 = st.selectbox("Axe X", list(numeric_features.keys()),
                                       format_func=lambda x: numeric_features[x],
                                       key="x4", index=3)  # efficiency_wh_per_km
            with col_y4:
                y_axis_4 = st.selectbox("Axe Y", list(numeric_features.keys()),
                                       format_func=lambda x: numeric_features[x],
                                       key="y4", index=4)  # range_km
            with col_c4:
                color_4 = st.selectbox("Couleur", ["segment", "brand"], key="c4")
            
            df_plot4 = df_all_features.dropna(subset=[x_axis_4, y_axis_4])
            
            if len(df_plot4) > 0:
                fig4 = px.scatter(df_plot4, x=x_axis_4, y=y_axis_4, color=color_4,
                                 hover_data=["brand", "model"],
                                 color_discrete_sequence=px.colors.qualitative.Pastel)
                fig4.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
                fig4.update_xaxes(title_text=numeric_features[x_axis_4])
                fig4.update_yaxes(title_text=numeric_features[y_axis_4])
                st.plotly_chart(fig4, use_container_width=True)
            else:
                st.warning("Pas assez de données pour ces axes")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Suggestions de comparaisons intéressantes
        st.markdown("---")
        st.markdown("### 💡 Suggestions de Comparaisons Intéressantes:")
        
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            st.info("**⚡ Performance**\n- Couple vs Vitesse Max\n- Accélération vs Puissance")
        with col_s2:
            st.info("**🔋 Efficacité**\n- Batterie vs Autonomie\n- Efficacité vs Autonomie")
        with col_s3:
            st.info("**📐 Design**\n- Longueur vs Cargo\n- Largeur vs Sièges")

    with tab5:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### Aperçu (50 lignes)")
        sql_preview = """
        SELECT brand, model, segment, range_km, battery_capacity_kWh, top_speed_kmh, drivetrain, seats
        FROM ev
        WHERE brand IN (SELECT UNNEST(?))
          AND segment IN (SELECT UNNEST(?))
        LIMIT 50;
        """
        st.dataframe(q(sql_preview, [brand_sel, segment_sel]), use_container_width=True, height=420)
        st.markdown("</div>", unsafe_allow_html=True)
