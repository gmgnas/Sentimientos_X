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

# --- ESTILO BASE ---
layout_base = dict(
    paper_bgcolor='#f4f7f6',       
    plot_bgcolor='#ffffff',        
    font=dict(color='#2c3e50', family="Arial", size=11),
    margin=dict(l=40, r=20, t=60, b=120) 
)

# 3. Leer Datos con FILTRO ESTRICTO (Solución al tema anterior)
conn = sqlite3.connect(db_path)
fecha_limite = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

# Usamos la cláusula WHERE para asegurar que solo traiga el tema actual
query = "SELECT * FROM tweets WHERE tema = ? AND date >= ?"
df = pd.read_sql_query(query, conn, params=(tema_actual, fecha_limite))
conn.close()

if df.empty:
    print(f"⚠️ No hay datos para el tema: '{tema_actual}' en los últimos 30 días.")
else:
    # --- PROCESAMIENTO PARA ORDEN CRONOLÓGICO ---
    df['fecha_dt'] = pd.to_datetime(df['date'])
    
    # Creamos una columna de solo fecha para agrupar, pero mantenemos el objeto datetime para ordenar
    df['fecha_agrupadora'] = df['fecha_dt'].dt.normalize()
    
    # Agrupamos por la fecha real (esto garantiza el orden matemático)
    df_agrupado = df.groupby(['fecha_agrupadora', 'sentimiento']).size().reset_index(name='cantidad')
    
    # Ordenamos el DataFrame explícitamente por fecha
    df_agrupado = df_agrupado.sort_values('fecha_agrupadora')
    
    # Creamos la etiqueta para el eje X DESPUÉS de ordenar
    df_agrupado['etiqueta_eje'] = df_agrupado['fecha_agrupadora'].dt.strftime('%d-%b')

    # 4. Gráfico de Tendencia (Corrección de Orden)
    fig_col = px.bar(df_agrupado, 
                      x='etiqueta_eje', 
                      y='cantidad', 
                      color='sentimiento',
                      title=f'Análisis Diario: {tema_actual}',
                      color_discrete_map=color_map,
                      barmode='stack',
                      template="plotly_white",
                      # Esta línea asegura que Plotly respete el orden del DataFrame
                      category_orders={"etiqueta_eje": df_agrupado['etiqueta_eje'].unique().tolist()})

    fig_col.update_layout(
        **layout_base,
        autosize=True,
        height=500,
        bargap=0.4,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="top", y=-0.3, xanchor="center", x=0.5, title_text='')
    )
    
    fig_col.update_xaxes(
        type='category', 
        tickangle=-45, 
        tickfont=dict(size=10),
        rangeslider_visible=False,
        showgrid=False
    )
    
    fig_col.write_html(os.path.join(docs_dir, 'lineas.html'), full_html=False, include_plotlyjs='cdn')

    # 5. Gráfico de Torta
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
    
    fig_torta.write_html(os.path.join(docs_dir, 'torta.html'), full_html=False, include_plotlyjs='cdn')

    # 6. data.js
    with open(os.path.join(docs_dir, 'data.js'), 'w', encoding='utf-8') as f:
        f.write(f"const total = {len(df)}; const pos = {len(df[df.sentimiento == 'Positivo'])}; const neu = {len(df[df.sentimiento == 'Neutral'])}; const neg = {len(df[df.sentimiento == 'Negativo'])}; const temaActual = '{tema_actual}';")

    print(f"📊 Dashboard actualizado y ordenado para '{tema_actual}'.")