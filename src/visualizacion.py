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

# --- ESTILO DE ALTO IMPACTO (FONDO GRIS CLARO E INSTITUCIONAL) ---
layout_base = dict(
    paper_bgcolor='#f4f7f6',       # Fondo del recuadro (gris suave)
    plot_bgcolor='#ffffff',        # Fondo del área de datos (blanco para contraste)
    font=dict(color='#2c3e50', family="Arial", size=12),
    title_font=dict(size=20, family='Arial Black', color='#1a1a1a'),
    margin=dict(l=50, r=50, t=80, b=100) # Margen inferior amplio para la leyenda
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

    # 4. Gráfico de Tendencia Temporal (MÁS ANCHO Y LEYENDA ABAJO)
    fig_col = px.bar(df_agrupado, 
                      x='dia_mes', 
                      y='cantidad', 
                      color='sentimiento',
                      title=f'Evolución Diaria: {tema_actual}',
                      color_discrete_map=color_map,
                      barmode='stack',
                      template="plotly_white",
                      labels={'dia_mes': 'Fecha', 'cantidad': 'Posts'})

    fig_col.update_layout(
        **layout_base,
        width=1100,  # Recuadro más ancho para evitar scroll horizontal
        height=550,  # Altura suficiente para eliminar scroll vertical
        bargap=0.2,
        # RÓTULO DE DATOS (LEYENDA) ABAJO Y CENTRADO
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5,
            title_text='' 
        )
    )
    
    # Quitar barra deslizante (rangeslider) para limpiar la visualización
    fig_col.update_xaxes(rangeslider_visible=False, type='category', showgrid=False)
    fig_col.update_yaxes(gridcolor='#eeeeee', zeroline=False)

    fig_col.write_html(os.path.join(docs_dir, 'lineas.html'), full_html=False, include_plotlyjs='cdn')

    # 5. Gráfico de Distribución de Sentimientos (TORTA)
    df_sent = df['sentimiento'].value_counts().reset_index()
    df_sent.columns = ['sentimiento', 'cantidad']
    
    fig_torta = px.pie(df_sent, values='cantidad', names='sentimiento', 
                      title='Total %',
                      color='sentimiento', 
                      color_discrete_map=color_map, 
                      hole=0.4)
    
    fig_torta.update_layout(
        **layout_base,
        width=400,   # Recuadro más angosto y proporcional
        height=550,  # Misma altura que el de barras para simetría
        showlegend=True,
        legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5)
    )
    
    fig_torta.update_traces(marker=dict(line=dict(color='#f4f7f6', width=2)))

    fig_torta.write_html(os.path.join(docs_dir, 'torta.html'), full_html=False, include_plotlyjs='cdn')

    # 6. Actualizar data.js (Para los contadores superiores)
    total = len(df)
    pos = len(df[df.sentimiento == 'Positivo'])
    neu = len(df[df.sentimiento == 'Neutral'])
    neg = len(df[df.sentimiento == 'Negativo'])

    with open(os.path.join(docs_dir, 'data.js'), 'w', encoding='utf-8') as f:
        f.write(f"const total = {total}; const pos = {pos}; const neu = {neu}; const neg = {neg}; const temaActual = '{tema_actual}';")

    print(f"📊 Dashboard actualizado para: {tema_actual}")