import pandas as pd
import sqlite3
import plotly.express as px
import os
import yaml

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

# --- CONFIGURACIÓN DE ESTILO DE ALTO IMPACTO ---
layout_estilizado = dict(
    paper_bgcolor='rgba(0,0,0,0)', # Transparente para fundirse con la web
    plot_bgcolor='#f8f9fa',       # Fondo gris muy tenue y limpio
    font=dict(color='#2c3e50', family="Arial", size=12),
    title_font=dict(size=20, family='Arial Black', color='#1a1a1a'),
    margin=dict(l=40, r=40, t=60, b=40)
)

# 3. Leer y FILTRAR Datos
conn = sqlite3.connect(db_path)
query = f"SELECT * FROM tweets WHERE tema = '{tema_actual}'"
df = pd.read_sql_query(query, conn)
conn.close()

if df.empty:
    print(f"❌ No hay datos para el tema: {tema_actual}")
else:
    # --- PROCESAMIENTO ---
    df['fecha_dt'] = pd.to_datetime(df['date'])
    df['dia_mes'] = df['fecha_dt'].dt.strftime('%d-%b')
    
    df = df.sort_values('fecha_dt')
    df_agrupado = df.groupby(['dia_mes', 'sentimiento', 'fecha_dt']).size().reset_index(name='cantidad')
    df_agrupado = df_agrupado.sort_values('fecha_dt')

    # 4. Gráfico de Columnas Segmentadas (ANCHO Y PROPORCIONAL)
    fig_col = px.bar(df_agrupado, 
                      x='dia_mes', 
                      y='cantidad', 
                      color='sentimiento',
                      title=f'Evolución Diaria: {tema_actual}',
                      color_discrete_map=color_map,
                      barmode='stack',
                      template="plotly_white",
                      labels={'dia_mes': 'Fecha', 'cantidad': 'Cantidad de Posts'})

    fig_col.update_layout(
        **layout_estilizado,
        width=900,  # Mayor ancho para impacto visual
        height=500,
        bargap=0.15
    )
    
    # Pulido de ejes
    fig_col.update_xaxes(type='category', showgrid=False, linecolor='#dcdde1')
    fig_col.update_yaxes(gridcolor='#ecf0f1', zeroline=False)

    fig_col.write_html(os.path.join(docs_dir, 'lineas.html'), full_html=False, include_plotlyjs='cdn')

    # 5. Gráfico de Torta (ANGOSTO Y MINIMALISTA)
    df_sent = df['sentimiento'].value_counts().reset_index()
    df_sent.columns = ['sentimiento', 'cantidad']
    
    fig_torta = px.pie(df_sent, values='cantidad', names='sentimiento', 
                      title=f'Distribución Total',
                      color='sentimiento', 
                      color_discrete_map=color_map, 
                      hole=0.4)
    
    fig_torta.update_layout(
        **layout_estilizado,
        width=400,  # Más angosto
        height=450,
        showlegend=True
    )
    
    # Separación elegante entre porciones
    fig_torta.update_traces(marker=dict(line=dict(color='#FFFFFF', width=2)))

    fig_torta.write_html(os.path.join(docs_dir, 'torta.html'), full_html=False, include_plotlyjs='cdn')

    # 6. Actualizar data.js
    total = len(df)
    pos = len(df[df.sentimiento == 'Positivo'])
    neu = len(df[df.sentimiento == 'Neutral'])
    neg = len(df[df.sentimiento == 'Negativo'])

    with open(os.path.join(docs_dir, 'data.js'), 'w', encoding='utf-8') as f:
        f.write(f"const total = {total}; const pos = {pos}; const neu = {neu}; const neg = {neg}; const temaActual = '{tema_actual}';")

    print(f"📊 Dashboard actualizado para: {tema_actual} ({total} posts procesados).")