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

# 2. Cargar Configuración (Vital para el nombre dinámico)
with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

tema_actual = config['analisis']['query'] # Leemos el tema del config

color_map = {
    'Positivo': config['estetica']['pos'],
    'Neutral': config['estetica']['neu'],
    'Negativo': config['estetica']['neg']
}

# 3. Leer y FILTRAR Datos
conn = sqlite3.connect(db_path)
# Filtramos por el tema actual para que no se mezclen en el gráfico
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
    # Tomamos solo los últimos 30 días si hubiera más
    df_agrupado = df.groupby(['dia_mes', 'sentimiento', 'fecha_dt']).size().reset_index(name='cantidad')
    df_agrupado = df_agrupado.sort_values('fecha_dt')

    # 4. Gráfico de Columnas Segmentadas
    fig_col = px.bar(df_agrupado, 
                      x='dia_mes', 
                      y='cantidad', 
                      color='sentimiento',
                      title=f'Evolución Diaria: {tema_actual}', # Usamos el tema del config
                      color_discrete_map=color_map,
                      barmode='stack',
                      template="plotly_white",
                      labels={'dia_mes': 'Fecha', 'cantidad': 'Cantidad de Posts'})

    fig_col.update_xaxes(type='category')
    fig_col.write_html(os.path.join(docs_dir, 'lineas.html'), full_html=False, include_plotlyjs='cdn')

    # 5. Gráfico de Torta
    df_sent = df['sentimiento'].value_counts().reset_index()
    df_sent.columns = ['sentimiento', 'cantidad']
    fig_torta = px.pie(df_sent, values='cantidad', names='sentimiento', 
                      title=f'Distribución Total: {tema_actual}',
                      color='sentimiento', 
                      color_discrete_map=color_map, 
                      hole=0.4)
    fig_torta.write_html(os.path.join(docs_dir, 'torta.html'), full_html=False, include_plotlyjs='cdn')

    # 6. Actualizar data.js (Para los contadores superiores)
    total = len(df)
    pos = len(df[df.sentimiento == 'Positivo'])
    neu = len(df[df.sentimiento == 'Neutral'])
    neg = len(df[df.sentimiento == 'Negativo'])

    with open(os.path.join(docs_dir, 'data.js'), 'w', encoding='utf-8') as f:
        f.write(f"const total = {total}; const pos = {pos}; const neu = {neu}; const neg = {neg}; const temaActual = '{tema_actual}';")

    print(f"📊 Dashboard actualizado para: {tema_actual} ({total} posts procesados).")