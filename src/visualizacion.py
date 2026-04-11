import pandas as pd
import sqlite3
import plotly.express as px
import os
import yaml

# Cargar rutas y config
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(base_dir, 'data', 'sentimientos.db')
config_path = os.path.join(base_dir, 'src', 'config.yaml')

with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Colores desde el config
color_map = {
    'Positivo': config['estetica']['pos'],
    'Neutral': config['estetica']['neu'],
    'Negativo': config['estetica']['neg']
}

# Leer Base de Datos
conn = sqlite3.connect(db_path)
df = pd.read_sql_query("SELECT * FROM tweets", conn)
df['date'] = pd.to_datetime(df['date'])
conn.close()

# 1. Gráfico de Evolución Temporal (Líneas)
df_diario = df.resample('D', on='date').size().reset_index(name='cantidad')
fig_linea = px.line(df_diario, x='date', y='cantidad', title='Frecuencia de Posteos (30 días)')
fig_linea.update_traces(line_color=config['estetica']['pos'])
fig_linea.write_html(os.path.join(base_dir, 'docs', 'lineas.html'), full_html=False, include_plotlyjs='cdn')

# 2. Cálculo de Métricas para Tarjetas
total = len(df)
pos = len(df[df.sentimiento == 'Positivo'])
neu = len(df[df.sentimiento == 'Neutral'])
neg = len(df[df.sentimiento == 'Negativo'])

# Exportar datos para el Dashboard
with open(os.path.join(base_dir, 'docs', 'data.js'), 'w') as f:
    f.write(f"const total={total}; const pos={pos}; const neu={neu}; const neg={neg};")

print("✅ Dashboard actualizado correctamente.")