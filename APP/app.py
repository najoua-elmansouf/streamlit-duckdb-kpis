import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Get the parent directory of APP folder to access data
DB_PATH = r"c:\Users\masis.zovikoglu\streamlit-duckdb-kpis-1\data\project.db"

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
    if x is None or pd.isna(x):
        return "—"
    return f"{x:,.0f}".replace(",", " ")

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

    tab1, tab2, tab3, tab4 = st.tabs(["📈 Vue KPI", "🏬 Comparaison Stores", "📊 Analyses Avancées", "🧾 Détails"])

    with tab1:
        c1, c2 = st.columns([0.65, 0.35], gap="large")

        with c1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
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
            st.markdown("</div>", unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("### Holiday vs Non-Holiday")
            # Make labels nicer
            df_holiday2 = df_holiday.copy()
            df_holiday2["Holiday"] = df_holiday2["Holiday_Flag"].map({0: "Non-Holiday", 1: "Holiday"})
            fig2 = px.pie(df_holiday2, names="Holiday", values="total_sales", hole=0.45,
                         color_discrete_sequence=['#1E78FF', '#5AA9FF'])
            fig2.update_layout(height=420, margin=dict(l=10, r=10, t=50, b=10))
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### Classement des stores (ventes totales)")
        fig3 = px.bar(df_store.head(15), x="Store_Number", y="total_sales",
                     color="total_sales", color_continuous_scale="Blues")
        fig3.update_layout(height=420, margin=dict(l=10, r=10, t=50, b=10), 
                          xaxis_title="Store", yaxis_title="Total ventes")
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.markdown("### 📊 Analyses Avancées")
        
        # Ligne 1: Top/Bottom Performers et Holiday Impact
        col1, col2 = st.columns(2, gap="large")
        
        with col1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("#### � Top 10 vs Bottom 10 Stores")
            
            # Préparer top et bottom
            top_10 = df_performance.head(10).copy()
            top_10['Category'] = 'Top 10'
            bottom_10 = df_performance.tail(10).copy()
            bottom_10['Category'] = 'Bottom 10'
            
            df_top_bottom = pd.concat([top_10, bottom_10])
            
            fig_perf = px.bar(df_top_bottom, 
                             x="Store_Number", 
                             y="total_sales",
                             color="Category",
                             color_discrete_map={'Top 10': '#1E78FF', 'Bottom 10': '#FF6B6B'},
                             barmode='group')
            
            fig_perf.update_layout(height=350, margin=dict(l=10, r=10, t=30, b=10))
            fig_perf.update_xaxes(title_text="Store Number")
            fig_perf.update_yaxes(title_text="Total Ventes ($)")
            
            st.plotly_chart(fig_perf, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("#### 🎉 Impact des Jours Fériés par Store")
            
            # Pivot pour comparer
            df_pivot = df_holiday_impact.pivot(index="Store_Number", columns="Holiday_Flag", values="avg_sales")
            if 0 in df_pivot.columns and 1 in df_pivot.columns:
                df_pivot['Impact'] = ((df_pivot[1] - df_pivot[0]) / df_pivot[0] * 100).round(1)
                df_pivot = df_pivot.sort_values('Impact', ascending=False).head(10)
                
                fig_impact = px.bar(df_pivot.reset_index(), 
                                   x="Store_Number", 
                                   y="Impact",
                                   color="Impact",
                                   color_continuous_scale=["#FF6B6B", "#FFEB3B", "#4ECDC4"])
                
                fig_impact.update_layout(height=350, margin=dict(l=10, r=10, t=30, b=10))
                fig_impact.update_xaxes(title_text="Store Number")
                fig_impact.update_yaxes(title_text="Impact Holiday (%)")
                
                st.plotly_chart(fig_impact, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Ligne 2: Distribution et Tendance comparative
        col3, col4 = st.columns(2, gap="large")
        
        with col3:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("#### 📦 Distribution des Ventes (Box Plot)")
            
            df_distribution["Holiday"] = df_distribution["Holiday_Flag"].map({0: "Non-Holiday", 1: "Holiday"})
            fig_box = px.box(df_distribution, x="Holiday", y="sales",
                           color="Holiday",
                           color_discrete_sequence=['#1E78FF', '#FF6B6B'])
            fig_box.update_layout(height=350, margin=dict(l=10, r=10, t=30, b=10),
                                showlegend=False)
            fig_box.update_yaxes(title_text="Ventes hebdomadaires ($)")
            
            st.plotly_chart(fig_box, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("#### 📈 Tendance: Top 5 Stores")
            
            # Sélectionner top 5 stores
            top_5_stores = df_performance.head(5)['Store_Number'].tolist()
            df_top5_trend = df_weekly_perf[df_weekly_perf['Store_Number'].isin(top_5_stores)]
            
            fig_trend = px.line(df_top5_trend, 
                               x="Date", 
                               y="sales",
                               color="Store_Number",
                               color_discrete_sequence=px.colors.sequential.Blues_r)
            
            fig_trend.update_layout(height=350, margin=dict(l=10, r=10, t=30, b=10))
            fig_trend.update_xaxes(title_text="Date")
            fig_trend.update_yaxes(title_text="Ventes ($)")
            
            st.plotly_chart(fig_trend, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
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

    tab1, tab2, tab3, tab4 = st.tabs(["🚗 Top Autonomie", "🏷️ Marques", "📊 Analyses Avancées", "🧾 Détails"])

    with tab1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### Top 10 autonomies (filtré)")
        sql_top = """
        SELECT brand, model, range_km
        FROM ev
        WHERE brand IN (SELECT UNNEST(?))
          AND segment IN (SELECT UNNEST(?))
          AND range_km IS NOT NULL
        ORDER BY range_km DESC
        LIMIT 10;
        """
        df_top = q(sql_top, [brand_sel, segment_sel])
        fig = px.bar(df_top, x="model", y="range_km", hover_data=["brand"],
                    color="range_km", color_continuous_scale="Blues")
        fig.update_layout(height=420, margin=dict(l=10, r=10, t=50, b=10), xaxis_title="Modèle", yaxis_title="Autonomie (km)")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### Autonomie moyenne par marque")
        sql_avg = """
        SELECT brand, AVG(range_km) AS avg_range_km
        FROM ev
        WHERE brand IN (SELECT UNNEST(?))
          AND segment IN (SELECT UNNEST(?))
          AND range_km IS NOT NULL
        GROUP BY brand
        ORDER BY avg_range_km DESC;
        """
        df_avg = q(sql_avg, [brand_sel, segment_sel])
        fig2 = px.bar(df_avg, x="brand", y="avg_range_km",
                     color="avg_range_km", color_continuous_scale="Blues")
        fig2.update_layout(height=420, margin=dict(l=10, r=10, t=50, b=10), xaxis_title="Marque", yaxis_title="Autonomie moyenne (km)")
        st.plotly_chart(fig2, use_container_width=True)
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
            st.markdown("#### ⚡ Autonomie vs Capacité Batterie")
            
            fig_scatter = px.scatter(df_scatter, 
                                    x="battery_capacity_kWh", 
                                    y="range_km",
                                    color="segment",
                                    size="top_speed_kmh",
                                    hover_data=["brand", "model"],
                                    color_discrete_sequence=px.colors.qualitative.Set2)
            
            fig_scatter.update_layout(height=350, margin=dict(l=10, r=10, t=30, b=10))
            fig_scatter.update_xaxes(title_text="Capacité Batterie (kWh)")
            fig_scatter.update_yaxes(title_text="Autonomie (km)")
            
            st.plotly_chart(fig_scatter, use_container_width=True)
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
            
            fig_speed = px.histogram(df_speed, 
                                    x="top_speed_kmh",
                                    nbins=30,
                                    color_discrete_sequence=['#1E78FF'])
            
            fig_speed.update_layout(height=350, margin=dict(l=10, r=10, t=30, b=10))
            fig_speed.update_xaxes(title_text="Vitesse Max (km/h)")
            fig_speed.update_yaxes(title_text="Nombre de modèles")
            
            st.plotly_chart(fig_speed, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("#### 🎯 Bubble Chart Multi-Dimensions")
            
            # Top 20 pour lisibilité
            df_bubble = df_scatter.nlargest(20, 'range_km')
            
            fig_bubble = px.scatter(df_bubble,
                                   x="battery_capacity_kWh",
                                   y="top_speed_kmh",
                                   size="range_km",
                                   color="brand",
                                   hover_name="model",
                                   size_max=60)
            
            fig_bubble.update_layout(height=350, margin=dict(l=10, r=10, t=30, b=10))
            fig_bubble.update_xaxes(title_text="Batterie (kWh)")
            fig_bubble.update_yaxes(title_text="Vitesse Max (km/h)")
            
            st.plotly_chart(fig_bubble, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
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
