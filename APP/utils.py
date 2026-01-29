"""
Utility functions for the Streamlit Dashboard
Reduces code repetition and improves maintainability
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from contextlib import contextmanager


# ========================================
# CONTEXT MANAGERS (for cleaner code)
# ========================================

@contextmanager
def section_card():
    """Context manager for section cards - automatically opens and closes the div"""
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    try:
        yield
    finally:
        st.markdown("</div>", unsafe_allow_html=True)


# ========================================
# FORMATTING FUNCTIONS
# ========================================

def format_number(value, prefix="$", suffix=""):
    """
    Format a number with thousand separators and optional prefix/suffix
    
    Args:
        value: The number to format
        prefix: String to add before the number (default: "$")
        suffix: String to add after the number (default: "")
    
    Returns:
        Formatted string
    """
    if pd.isna(value):
        return "N/A"
    return f"{prefix}{value:,.0f}{suffix}"


def create_scatter_plot(df, x, y, color=None, hover_data=None, 
                       color_scale=None, title_x=None, title_y=None, 
                       height=300, color_discrete_sequence=None):
    """
    Create a standardized scatter plot
    
    Args:
        df: DataFrame with data
        x: Column name for x-axis
        y: Column name for y-axis
        color: Column name for color grouping
        hover_data: List of columns to show on hover
        color_scale: Color scale for continuous data
        title_x: X-axis title
        title_y: Y-axis title
        height: Figure height in pixels
        color_discrete_sequence: List of colors for discrete data
    
    Returns:
        Plotly figure
    """
    fig = px.scatter(
        df, x=x, y=y, color=color,
        hover_data=hover_data or [],
        color_continuous_scale=color_scale,
        color_discrete_sequence=color_discrete_sequence
    )
    
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=10, b=10)
    )
    
    if title_x:
        fig.update_xaxes(title_text=title_x)
    if title_y:
        fig.update_yaxes(title_text=title_y)
    
    return fig


def create_bar_chart(df, x, y, color=None, color_map=None, 
                    title_x=None, title_y=None, height=280, 
                    show_text=True, text_position='outside'):
    """
    Create a standardized bar chart
    
    Args:
        df: DataFrame with data
        x: Column name for x-axis
        y: Column name for y-axis
        color: Column name for color grouping
        color_map: Dictionary mapping colors to values
        title_x: X-axis title
        title_y: Y-axis title
        height: Figure height in pixels
        show_text: Whether to show values on bars
        text_position: Position of text labels
    
    Returns:
        Plotly figure
    """
    fig = px.bar(
        df, x=x, y=y, color=color,
        color_discrete_map=color_map,
        text=y if show_text else None
    )
    
    if show_text:
        fig.update_traces(textposition=text_position)
    
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=bool(color)
    )
    
    if title_x:
        fig.update_xaxes(title_text=title_x)
    if title_y:
        fig.update_yaxes(title_text=title_y)
    
    return fig


def create_line_chart(df, x, y, color=None, markers=True,
                     title_x=None, title_y=None, height=420,
                     color_sequence=None):
    """
    Create a standardized line chart
    
    Args:
        df: DataFrame with data
        x: Column name for x-axis
        y: Column name for y-axis
        color: Column name for color grouping
        markers: Whether to show markers on the line
        title_x: X-axis title
        title_y: Y-axis title
        height: Figure height in pixels
        color_sequence: List of colors
    
    Returns:
        Plotly figure
    """
    fig = px.line(
        df, x=x, y=y, color=color,
        markers=markers,
        color_discrete_sequence=color_sequence
    )
    
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    if title_x:
        fig.update_xaxes(title_text=title_x)
    if title_y:
        fig.update_yaxes(title_text=title_y)
    
    return fig


def create_kpi_card(label, value, subtitle=None):
    """
    Create HTML for a KPI card
    
    Args:
        label: The KPI label/title
        value: The KPI value to display
        subtitle: Optional subtitle text
    
    Returns:
        HTML string
    """
    subtitle_html = f'<div class="kpi-sub">{subtitle}</div>' if subtitle else ''
    
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {subtitle_html}
    </div>
    """


def create_section_card(title, content):
    """
    Create HTML for a section card
    
    Args:
        title: Section title
        content: Section content (can be HTML)
    
    Returns:
        HTML string
    """
    return f"""
    <div class="section-card">
        <h4>{title}</h4>
        {content}
    </div>
    """


def categorize_performance(df, value_column, categories=3):
    """
    Categorize performance into levels (Low, Medium, High)
    
    Args:
        df: DataFrame with data
        value_column: Column name to use for categorization
        categories: Number of categories (default: 3)
    
    Returns:
        DataFrame with added 'Catégorie' column
    """
    if categories == 3:
        q33 = df[value_column].quantile(0.33)
        q66 = df[value_column].quantile(0.66)
        
        def categorize(value):
            if value < q33:
                return "⚠️ Faible"
            elif value < q66:
                return "✅ Moyen"
            else:
                return "🌟 Élevé"
        
        df['Catégorie'] = df[value_column].apply(categorize)
        return df, q33, q66
    
    return df, None, None


def create_comparison_selector(features_dict, key_prefix, default_x=0, default_y=1):
    """
    Create a pair of selectboxes for choosing X and Y axes
    
    Args:
        features_dict: Dictionary of feature_key: feature_label
        key_prefix: Unique prefix for widget keys
        default_x: Default index for X axis
        default_y: Default index for Y axis
    
    Returns:
        Tuple of (x_selected, y_selected)
    """
    col_x, col_y = st.columns(2)
    
    with col_x:
        x_axis = st.selectbox(
            "Axe X",
            list(features_dict.keys()),
            format_func=lambda x: features_dict[x],
            key=f"x_{key_prefix}",
            index=default_x
        )
    
    with col_y:
        y_axis = st.selectbox(
            "Axe Y",
            list(features_dict.keys()),
            format_func=lambda x: features_dict[x],
            key=f"y_{key_prefix}",
            index=default_y
        )
    
    return x_axis, y_axis


def create_scatter_comparison_chart(df, x, y, color_by, features_dict, 
                                    hover_cols=None, color_scale="Blues",
                                    title=None):
    """
    Create a complete scatter chart with selectors for comparison
    Reduces the repetitive code in tab4 sections
    
    Args:
        df: DataFrame with data
        x: Selected x-axis column
        y: Selected y-axis column
        color_by: Column for coloring
        features_dict: Dictionary of feature names
        hover_cols: Columns to show on hover
        color_scale: Plotly color scale
        title: Optional chart title
    
    Returns:
        Plotly figure or None if insufficient data
    """
    df_plot = df.dropna(subset=[x, y])
    
    if len(df_plot) == 0:
        st.warning("Pas assez de données pour ces axes")
        return None
    
    fig = create_scatter_plot(
        df_plot, x=x, y=y, color=color_by,
        hover_data=hover_cols or [],
        color_scale=color_scale,
        title_x=features_dict.get(x, x),
        title_y=features_dict.get(y, y)
    )
    
    return fig


def render_comparison_quadrant(df, features_dict, chart_num, 
                               default_x, default_y, color_by,
                               hover_cols=None, color_scale="Blues"):
    """
    Render one quadrant of the 2x2 comparison grid
    Drastically reduces repetition in comparator tabs
    
    Args:
        df: DataFrame with data
        features_dict: Dict of feature_key: feature_label
        chart_num: Chart number (1-4)
        default_x: Default index for X selector
        default_y: Default index for Y selector
        color_by: Column name for coloring
        hover_cols: Columns to display on hover
        color_scale: Plotly color scale name
    """
    with section_card():
        st.markdown(f"#### 📊 Graphique {chart_num}")
        
        # Create selectors
        x_axis, y_axis = create_comparison_selector(
            features_dict,
            key_prefix=f"chart{chart_num}",
            default_x=default_x,
            default_y=default_y
        )
        
        # Create and display chart
        fig = create_scatter_comparison_chart(
            df, x_axis, y_axis, color_by, features_dict,
            hover_cols=hover_cols, color_scale=color_scale
        )
        
        if fig:
            st.plotly_chart(fig, use_container_width=True)


# ========================================
# SQL QUERY HELPERS
# ========================================

def clean_numeric_column(col_name):
    """
    Generate SQL to clean a numeric column (remove commas, cast to DOUBLE)
    
    Args:
        col_name: Column name to clean
    
    Returns:
        SQL expression string
    """
    return f"CAST(REPLACE({col_name}, ',', '') AS DOUBLE)"


# ========================================
# LAYOUT HELPERS
# ========================================

def create_2x2_comparison_grid(df, features_dict, color_by, hover_cols=None,
                               defaults=None, color_scales=None):
    """
    Create a complete 2x2 grid of comparison charts
    Massively reduces code repetition
    
    Args:
        df: DataFrame with all data
        features_dict: Dict of available features
        color_by: Column to color by
        hover_cols: Columns to show on hover
        defaults: List of tuples [(x_idx1, y_idx1), (x_idx2, y_idx2), ...]
        color_scales: List of color scale names for each chart
    """
    if defaults is None:
        defaults = [(1, 4), (0, 5), (2, 0), (3, 4)]
    
    if color_scales is None:
        color_scales = ["Blues", "Teal", "Sunset", "Purp"]
    
    # Row 1
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        render_comparison_quadrant(
            df, features_dict, 1, defaults[0][0], defaults[0][1],
            color_by, hover_cols, color_scales[0]
        )
    
    with col2:
        render_comparison_quadrant(
            df, features_dict, 2, defaults[1][0], defaults[1][1],
            color_by, hover_cols, color_scales[1]
        )
    
    # Row 2
    col3, col4 = st.columns(2, gap="large")
    
    with col3:
        render_comparison_quadrant(
            df, features_dict, 3, defaults[2][0], defaults[2][1],
            color_by, hover_cols, color_scales[2]
        )
    
    with col4:
        render_comparison_quadrant(
            df, features_dict, 4, defaults[3][0], defaults[3][1],
            color_by, hover_cols, color_scales[3]
        )


def create_comparison_suggestions(walmart=True):
    """
    Display suggestion cards for interesting comparisons
    
    Args:
        walmart: True for Walmart suggestions, False for EV suggestions
    """
    st.markdown("---")
    st.markdown("### 💡 Suggestions de Comparaisons Intéressantes:")
    
    col_s1, col_s2, col_s3 = st.columns(3)
    
    if walmart:
        with col_s1:
            st.info("**💰 Performance**\n- Ventes vs Impact Holiday\n- Ventes vs Nombre Semaines")
        with col_s2:
            st.info("**📊 Économie**\n- Chômage vs Ventes\n- CPI vs Ventes\n- Prix Carburant vs Ventes")
        with col_s3:
            st.info("**🎯 Stratégie**\n- Jours Fériés vs Impact\n- Ventes Holiday vs Regular")
    else:
        with col_s1:
            st.info("**⚡ Performance**\n- Couple vs Vitesse Max\n- Accélération vs Puissance")
        with col_s2:
            st.info("**🔋 Efficacité**\n- Batterie vs Autonomie\n- Efficacité vs Autonomie")
        with col_s3:
            st.info("**📐 Design**\n- Longueur vs Cargo\n- Largeur vs Sièges")


# Import pandas for the format_number function
