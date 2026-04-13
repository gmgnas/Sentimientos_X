import pandas as pd
import sqlite3
import plotly.express as px
import os
import yaml
from datetime import datetime, timedelta

# 1. Configuración de Rutas
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(base_dir, 'data', 'sentimientos.db')
config_path = os.path.join(base_dir, 'src', 'config.yaml')
docs_dir = os.path.join(base_dir, 'docs')

with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

tema_actual = config['analisis']['query']
color_map = {'Positivo': config['estetica']['pos'], 'Neutral': config['estetica']['neu'], 'Negativo': config['estetica']['neg']}

# 2. Carga y Filtro
conn = sqlite3.connect(db_path)
fecha_limite = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
query = "SELECT * FROM tweets WHERE tema = ? AND date >= ?"
df = pd.read_sql_query(query, conn, params=(tema_actual, fecha_limite))
conn.close()

if not df.empty:
    df['fecha_dt'] = pd.to_datetime(df['date'])
    # Normalizamos a medianoche para agrupar por día real
    df['fecha_agrup'] = df['fecha_dt'].dt.normalize()
    
    # Agrupamos por la fecha real (esto mantiene el orden numérico)
    df_agrupado = df.groupby(['fecha_agrup', 'sentimiento']).size().reset_index(name='cantidad')
    df_agrupado = df_agrupado.sort_values('fecha_agrup')
    
    # Recién ahora creamos la etiqueta de texto para el eje X
    df_agrupado['dia_mes'] = df_agrupado['fecha_agrup'].dt.strftime('%d-%b')

    # 3. Gráfico de Tendencia
    fig_col = px.bar(df_agrupado, 
                      x='dia_mes', 
                      y='cantidad', 
                      color='sentimiento',
                      title=f'Evolución Diaria: {tema_actual}',
                      color_discrete_map=color_map,
                      template="plotly_white",
                      # Forzamos a Plotly a seguir el orden del DataFrame ordenado
                      category_orders={"dia_mes": df_agrupado['dia_mes'].unique().tolist()})

    fig_col.update_layout(
        paper_bgcolor='#f4f7f6', plot_bgcolor='#ffffff',
        autosize=True, height=500, bargap=0.4,
        margin=dict(l=40, r=20, t=60, b=120),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="top", y=-0.3, xanchor="center", x=0.5, title_text='')
    )
    
    fig_col.update_xaxes(type='category', tickangle=-45, tickfont=dict(size=10), rangeslider_visible=False)
    fig_col.write_html(os.path.join(docs_dir, 'lineas.html'), full_html=False, include_plotlyjs='cdn')

    # 4. Gráfico de Torta y data.js (Igual que antes...)
    # [Aquí iría el resto del código para la torta y data.js]
    print(f"📊 Dashboard actualizado para: {tema_actual} (30 días ordenados)")