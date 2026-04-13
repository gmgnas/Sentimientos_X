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

# Mapa de colores institucional desde config.yaml
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
    # --- PROCESAMIENTO DE DATOS ---
    
    # Convertimos a datetime y creamos una columna con formato "Día Mes" (ej: 13 Abr)
    # %d es el día, %b es el nombre del mes abreviado
    df['fecha_dt'] = pd.to_datetime(df['date'])
    df['dia_mes'] = df['fecha_dt'].dt.strftime('%d-%b')
    
    # Agrupamos por fecha y sentimiento para las columnas segmentadas
    # Ordenamos por la fecha real para que el gráfico mantenga el orden cronológico
    df = df.sort_values('fecha_dt')
    df_agrupado = df.groupby(['dia_mes', 'sentimiento', 'fecha_dt']).size().reset_index(name='cantidad')
    df_agrupado = df_agrupado.sort_values('fecha_dt')

    # 4. Gráfico de Columnas Segmentadas (Sustituye al de líneas)
    fig_col = px.bar(df_agrupado, 
                     x='dia_mes', 
                     y='cantidad', 
                     color='sentimiento',
                     title=f'Evolución Diaria: {df["tema"].iloc[0]}',
                     color_discrete_map=color_map,
                     barmode='stack', # Columnas apiladas
                     template="plotly_white",
                     labels={'dia_mes': 'Fecha', 'cantidad': 'Cantidad de Posts'})

    # Ajuste para que el eje X respete el orden de los días y no el alfabético
    fig_col.update_xaxes(type='category')
    
    # Guardamos como lineas.html para mantener compatibilidad con tu index.html
    fig_col.write_html(os.path.join(docs_dir, 'lineas.html'), full_html=False, include_plotlyjs='cdn')

    # 5. Gráfico de Torta (Se mantiene igual)
    df_sent = df['sentimiento'].value_counts().reset_index()
    df_sent.columns = ['sentimiento', 'cantidad']
    fig_torta = px.pie(df_sent, values='cantidad', names='sentimiento', 
                     title='Distribución Total de Sentimientos',
                     color='sentimiento', 
                     color_discrete_map=color_map, 
                     hole=0.4)
    fig_torta.write_html(os.path.join(docs_dir, 'torta.html'), full_html=False, include_plotlyjs='cdn')

    # 6. Actualizar data.js (Para los contadores superiores)
    total = len(df)
    pos = len(df[df.sentimiento == 'Positivo'])
    neu = len(df[df.sentimiento == 'Neutral'])
    neg = len(df[df.sentimiento == 'Negativo'])
    tema_actual = df["tema"].iloc[0]

    with open(os.path.join(docs_dir, 'data.js'), 'w', encoding='utf-8') as f:
        f.write(f"const total = {total}; const pos = {pos}; const neu = {neu}; const neg = {neg}; const temaActual = '{tema_actual}';")

    print(f"📊 Gráficos de columnas y torta generados en /docs con {total} posts.")