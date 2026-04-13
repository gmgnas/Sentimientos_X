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
    font=dict(color='#2c3e50', family="Arial", size=12),
    title_font=dict(size=20, family='Arial Black', color='#1a1a1a'),
    margin=dict(l=50, r=50, t=80, b=120) # Más margen inferior para la leyenda 30 días
)

# 3. Leer y FILTRAR Datos
conn = sqlite3.connect(db_path)
# Filtramos por tema y por los últimos 30 días desde hoy
fecha_limite = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
query = f"SELECT * FROM tweets WHERE tema = '{tema_actual}' AND date >= '{fecha_limite}'"
df = pd.read_sql_query(query, conn)
conn.close()

if df.empty:
    print(f"❌ No se encontraron datos para '{tema_actual}' en los últimos 30 días.")
else:
    # --- PROCESAMIENTO ---
    df['fecha_dt'] = pd.to_datetime(df['date'])
    df['dia_mes'] = df['fecha_dt'].dt.strftime('%d-%b')
    
    # Ordenamos cronológicamente para que el eje X fluya de izquierda a derecha
    df = df.sort_values('fecha_dt')
    
    df_agrupado = df.groupby(['dia_mes', 'sentimiento', 'fecha_dt']).size().reset_index(name='cantidad')
    df_agrupado = df_agrupado.sort_values('fecha_dt')

    # 4. Gráfico de Tendencia Temporal (30 DÍAS)
    fig_col = px.bar(df_agrupado, 
                      x='dia_mes', 
                      y='cantidad', 
                      color='sentimiento',
                      title=f'Tendencia Mensual: {tema_actual}',
                      color_discrete_map=color_map,
                      barmode='stack',
                      template="plotly_white",
                      labels={'dia_mes': 'Fecha', 'cantidad': 'Posts'})

    fig_col.update_layout(
        **layout_base,
        width=1100,  
        height=550,  
        bargap=0.3, # Barras un poco más finas para que entren 30 sin amontonarse
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.25, # Bajamos un poco más la leyenda por las etiquetas del eje X
            xanchor="center",
            x=0.5,
            title_text='' 
        )
    )
    
    # Ajuste fino del eje X para que no se amontone el texto
    fig_col.update_xaxes(
        rangeslider_visible=False, 
        type='category', 
        tickangle=-45, # Inclinamos las fechas para que se lean bien los 30 días
        showgrid=False
    )
    fig_col.update_yaxes(gridcolor='#eeeeee', zeroline=False)

    fig_col.write_html(os.path.join(docs_dir, 'lineas.html'), full_html=False, include_plotlyjs='cdn')

    # 5. Gráfico de Distribución (TORTA)
    df_sent = df['sentimiento'].value_counts().reset_index()
    df_sent.columns = ['sentimiento', 'cantidad']
    
    fig_torta = px.pie(df_sent, values='cantidad', names='sentimiento', 
                      title='Distribución 30 Días',
                      color='sentimiento', 
                      color_discrete_map=color_map, 
                      hole=0.4)
    
    fig_torta.update_layout(
        **layout_base,
        width=400,   
        height=550,  
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

    print(f"📊 Visualización de 30 días generada para: {tema_actual}")