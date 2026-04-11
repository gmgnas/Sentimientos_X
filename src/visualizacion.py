import pandas as pd
import sqlite3
import plotly.express as px
import os
import yaml

# 1. Configuración de Rutas
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(base_dir, 'data', 'sentimientos.db')
config_path = os.path.join(base_dir, 'src', 'config.yaml')

# 2. Cargar Configuración (Tema y Colores)
with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

tema_actual = config['analisis']['query']
# Mapeo de colores desde el config.yaml
color_map = {
    'Positivo': config['estetica']['pos'],
    'Neutral': config['estetica']['neu'],
    'Negativo': config['estetica']['neg']
}

# 3. Leer Datos desde SQLite
conn = sqlite3.connect(db_path)
df = pd.read_sql_query("SELECT * FROM tweets", conn)
df['date'] = pd.to_datetime(df['date'])
conn.close()

# 4. Generar Gráfico de Evolución Temporal
# Agrupamos por día para ver la frecuencia de posteos
df_diario = df.resample('D', on='date').size().reset_index(name='cantidad')

titulo_grafico = f'Evolución de Menciones en X<br><sub>Tema analizado: {tema_actual}</sub>'

fig_linea = px.line(
    df_diario, 
    x='date', 
    y='cantidad', 
    title=titulo_grafico,
    template="plotly_white"
)

# Ajustes estéticos del gráfico
fig_linea.update_traces(line_color=config['estetica']['pos'], line_width=3)
fig_linea.update_layout(
    title_x=0.5,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=20, r=20, t=60, b=20)
)

# Guardar el gráfico en la carpeta docs para el iframe
fig_linea.write_html(
    os.path.join(base_dir, 'docs', 'lineas.html'), 
    full_html=False, 
    include_plotlyjs='cdn'
)

# 5. Cálculo de Métricas para el Dashboard
total = len(df)
pos = len(df[df.sentimiento == 'Positivo'])
neu = len(df[df.sentimiento == 'Neutral'])
neg = len(df[df.sentimiento == 'Negativo'])

# 6. Exportar data.js (Conexión con index.html)
# Este archivo permite que el HTML muestre los números y el nombre del tema
with open(os.path.join(base_dir, 'docs', 'data.js'), 'w', encoding='utf-8') as f:
    f.write(f"const total = {total};\n")
    f.write(f"const pos = {pos};\n")
    f.write(f"const neu = {neu};\n")
    f.write(f"const neg = {neg};\n")
    f.write(f"const temaActual = '{tema_actual}';\n")

print(f"✅ Visualización generada exitosamente.")
print(f"📊 Tema: {tema_actual} | Total: {total} posts.")