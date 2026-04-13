import pandas as pd
import sqlite3
import plotly.express as px
import os
import yaml

# 1. Rutas
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(base_dir, 'data', 'sentimientos.db')
config_path = os.path.join(base_dir, 'src', 'config.yaml')
docs_dir = os.path.join(base_dir, 'docs') # Carpeta docs

# Crear carpeta docs si no existe
if not os.path.exists(docs_dir):
    os.makedirs(docs_dir)

# 2. Cargar Configuración
with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

color_map = {
    'Positivo': config['estetica']['pos'],
    'Neutral': config['estetica']['neu'],
    'Negativo': config['estetica']['neg']
}

# 3. Leer Datos
conn = sqlite3.connect(db_path)
df = pd.read_sql_query("SELECT * FROM tweets", conn)
conn.close()

if df.empty:
    print("❌ No hay datos para graficar.")
else:
    # --- LIMPIEZA DE FECHA (Solo día y año) ---
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    
    # 4. Gráfico de Líneas (Guardar en docs/)
    df_diario = df.groupby('date').size().reset_index(name='cantidad')
    fig_linea = px.line(df_diario, x='date', y='cantidad', 
                        title=f'Tendencia: {df["tema"].iloc[0]}',
                        template="plotly_white")
    fig_linea.update_traces(line_color=config['estetica']['pos'])
    fig_linea.write_html(os.path.join(docs_dir, 'lineas.html'), full_html=False, include_plotlyjs='cdn')

    # 5. Gráfico de Torta (Guardar en docs/)
    df_sent = df['sentimiento'].value_counts().reset_index()
    df_sent.columns = ['sentimiento', 'cantidad']
    fig_torta = px.pie(df_sent, values='cantidad', names='sentimiento', 
                     title='Distribución de Sentimientos',
                     color='sentimiento', color_discrete_map=color_map, hole=0.4)
    fig_torta.write_html(os.path.join(docs_dir, 'torta.html'), full_html=False, include_plotlyjs='cdn')

    # 6. Actualizar data.js (Guardar en docs/)
    total, pos, neu, neg = len(df), len(df[df.sentimiento=='Positivo']), len(df[df.sentimiento=='Neutral']), len(df[df.sentimiento=='Negativo'])
    tema_actual = df["tema"].iloc[0]

    with open(os.path.join(docs_dir, 'data.js'), 'w', encoding='utf-8') as f:
        f.write(f"const total = {total}; const pos = {pos}; const neu = {neu}; const neg = {neg}; const temaActual = '{tema_actual}';")

    print(f"📊 Gráficos generados en la carpeta /docs.")