import pandas as pd
import sqlite3
import plotly.express as px
import os
import yaml

# 1. Configuración de Rutas
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(base_dir, 'data', 'sentimientos.db')
config_path = os.path.join(base_dir, 'src', 'config.yaml')

# 2. Cargar Configuración y Colores
with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

tema_actual = config['analisis']['query']
color_map = {
    'Positivo': config['estetica']['pos'],
    'Neutral': config['estetica']['neu'],
    'Negativo': config['estetica']['neg']
}

# 3. Leer Datos
conn = sqlite3.connect(db_path)
df = pd.read_sql_query("SELECT * FROM tweets", conn)
df['date'] = pd.to_datetime(df['date'])
conn.close()

# --- 4. Gráfico de Líneas ---
df_diario = df.groupby('date').size().reset_index(name='cantidad')
fig_linea = px.line(df_diario, x='date', y='cantidad', title=f'Tendencia: {tema_actual}', template="plotly_white")
fig_linea.update_traces(line_color=config['estetica']['pos'])
fig_linea.write_html(os.path.join(base_dir, 'docs', 'lineas.html'), full_html=False, include_plotlyjs='cdn')

# --- 5. Gráfico de Torta (Proporciones) ---
df_sent = df['sentimiento'].value_counts().reset_index()
df_sent.columns = ['sentimiento', 'cantidad']

fig_torta = px.pie(df_sent, values='cantidad', names='sentimiento', 
                 title=f'Distribución de Sentimientos',
                 color='sentimiento', color_discrete_map=color_map,
                 hole=0.4, template="plotly_white")

fig_torta.update_traces(textinfo='percent+label')
fig_torta.write_html(os.path.join(base_dir, 'docs', 'torta.html'), full_html=False, include_plotlyjs='cdn')

# --- 6. Exportar data.js ---
total, pos, neu, neg = len(df), len(df[df.sentimiento=='Positivo']), len(df[df.sentimiento=='Neutral']), len(df[df.sentimiento=='Negativo'])

with open(os.path.join(base_dir, 'docs', 'data.js'), 'w', encoding='utf-8') as f:
    f.write(f"const total = {total}; const pos = {pos}; const neu = {neu}; const neg = {neg}; const temaActual = '{tema_actual}';")

print("📊 Gráficos y data.js actualizados correctamente.")