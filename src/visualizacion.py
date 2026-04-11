import pandas as pd
import sqlite3
import plotly.express as px
import os
import yaml

# Cargar rutas y config
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(base_dir, 'data', 'sentimientos.db')
config_path = os.path.join(base_dir, 'src', 'config.yaml')

# Cargar el archivo YAML con codificación UTF-8
with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# Extraer el tema dinámico según tu nueva estructura
tema_actual = config['analisis']['query']

# Colores Corporativos desde el config
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

# 1. Gráfico de Evolución Temporal con Título Dinámico
df_diario = df.resample('D', on='date').size().reset_index(name='cantidad')

# Título formateado con el tema Artemisa
titulo_grafico = f'Frecuencia de Posteos (30 días)<br><sub>Tema: {tema_actual}</sub>'

fig_linea = px.line(df_diario, x='date', y='cantidad', title=titulo_grafico)
fig_linea.update_traces(line_color=config['estetica']['pos'])
fig_linea.update_layout(
    title_x=0.5,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)

fig_linea.write_html(os.path.join(base_dir, 'docs', 'lineas.html'), full_html=False, include_plotlyjs='cdn')

# 2. Cálculo de Métricas para Tarjetas
total = len(df)
pos = len(df[df.sentimiento == 'Positivo'])
neu = len(df[df.sentimiento == 'Neutral'])
neg = len(df[df.sentimiento == 'Negativo'])

# Exportar datos para el Dashboard incluyendo la variable tema
with open(os.path.join(base_dir, 'docs', 'data.js'), 'w', encoding='utf-8') as f:
    f.write(f"const total={total}; ")
    f.write(f"const pos={pos}; ")
    f.write(f"const neu={neu}; ")
    f.write(f"const neg={neg}; ")
    f.write(f"const temaActual='{tema_actual}';")

print(f"✅ Dashboard actualizado correctamente para el tema: {tema_actual}")