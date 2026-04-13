import pandas as pd
import sqlite3
import plotly.express as px
import os
import yaml
from datetime import datetime, timedelta

# 1. Rutas
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(base_dir, 'data', 'sentimientos.db')
config_path = os.path.join(base_dir, 'src', 'config.yaml')
docs_dir = os.path.join(base_dir, 'docs')

if not os.path.exists(docs_dir):
    os.makedirs(docs_dir)

# 2. Cargar Configuración
with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

tema_actual = config['analisis']['query']

color_map = {
    'Positivo': config['estetica']['pos'],
    'Neutral': config['estetica']['neu'],
    'Negativo': config['estetica']['neg']
}

# --- ESTILO DE ALTO IMPACTO ---
layout_base = dict(
    paper_bgcolor='#f4f7f6',       
    plot_bgcolor='#ffffff',        
    font=dict(color='#2c3e50', family="Arial", size=11), # Fuente un poco más pequeña para ahorrar espacio
    title_font=dict(size=18, family='Arial Black', color='#1a1a1a'),
    margin=dict(l=40, r=20, t=60, b=100) 
)

# 3. Leer y FILTRAR Datos (Corrección: Filtro estricto de tema y fecha)
conn = sqlite3.connect(db_path)
fecha_limite = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

# IMPORTANTE: Usamos parámetros (?) para evitar errores con carácteres especiales y filtrar bien el tema
query = "SELECT * FROM tweets WHERE tema = ? AND date >= ?"
df = pd.read_sql_query(query, conn, params=(tema_actual, fecha_limite))
conn.close()

if df.empty:
    print(f"⚠️ No hay datos exclusivos para el tema: {tema_actual}")
else:
    # --- PROCESAMIENTO ---
    df['fecha_dt'] = pd.to_datetime(df['date'])
    # Agrupamos por fecha sin hora para separar las barras por día
    df['fecha_solo'] = df['fecha_dt'].dt.date
    df['etiqueta_eje'] = df['fecha_dt'].dt.strftime('%d-%b')
    
    df = df.sort_values('fecha_dt')
    
    # Agrupamos asegurando que el tema no se mezcle
    df_agrupado = df.groupby(['fecha_solo', 'etiqueta_eje', 'sentimiento']).size().reset_index(name='cantidad')
    df_agrupado = df_agrupado.sort_values('fecha_solo')

    # 4. Gráfico de Tendencia (AJUSTE DE ANCHO DINÁMICO)
    fig_col = px.bar(df_agrupado, 
                      x='etiqueta_eje', 
                      y='cantidad', 
                      color='sentimiento',
                      title=f'Análisis Diario: {tema_actual}',
                      color_discrete_map=color_map,
                      barmode='stack',
                      template="plotly_white")

    fig_col.update_layout(
        **layout_base,
        autosize=True,      # Permite que el gráfico use el ancho del contenedor HTML
        height=500,  
        bargap=0.4,         # Barras más delgadas para que entren los 30 días
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.25,
            xanchor="center",
            x=0.5,
            title_text='' 
        )
    )
    
    # Ajuste de etiquetas para que no se choquen
    fig_col.update_xaxes(
        type='category', 
        tickangle=-45, 
        tickfont=dict(size=10), # Fuente de fechas más pequeña
        rangeslider_visible=False,
        showgrid=False
    )
    
    fig_col.write_html(os.path.join(docs_dir, 'lineas.html'), full_html=False, include_plotlyjs='cdn')

    # 5. Gráfico de Torta (Distribución)
    df_sent = df['sentimiento'].value_counts().reset_index()
    df_sent.columns = ['sentimiento', 'cantidad']
    
    fig_torta = px.pie(df_sent, values='cantidad', names='sentimiento', 
                      title=f'Total 30 Días: {tema_actual}',
                      color='sentimiento', 
                      color_discrete_map=color_map, 
                      hole=0.4)
    
    fig_torta.update_layout(
        **layout_base,
        autosize=True,
        height=500,
        showlegend=True,
        legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5)
    )
    
    fig_torta.update_traces(marker=dict(line=dict(color='#f4f7f6', width=2)))
    fig_torta.write_html(os.path.join(docs_dir, 'torta.html'), full_html=False, include_plotlyjs='cdn')

    # 6. Actualizar data.js
    total = len(df)
    pos = len(df[df.sentimiento == 'Positivo'])
    neu = len(df[df.sentimiento == 'Neutral'])
    neg = len(df[df.sentimiento == 'Negativo'])

    with open(os.path.join(docs_dir, 'data.js'), 'w', encoding='utf-8') as f:
        f.write(f"const total = {total}; const pos = {pos}; const neu = {neu}; const neg = {neg}; const temaActual = '{tema_actual}';")

    print(f"📊 Dashboard filtrado por '{tema_actual}' y ajustado para 30 días.")