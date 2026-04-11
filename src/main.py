import sqlite3
import yaml
import os
import random
from datetime import datetime, timedelta

# 1. Rutas
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(base_dir, 'data', 'sentimientos.db')
config_path = os.path.join(base_dir, 'src', 'config.yaml')

# 2. Leer Configuración
with open(config_path, 'r') as file:
    config = yaml.safe_load(file)
tema = config['analisis']['query']

# 3. Conectar a Base de Datos (crea el archivo si no existe)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS tweets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tema TEXT,
        date TEXT,
        sentimiento TEXT
    )
''')

# 4. Insertar datos (Aquí conectan la API real de X en el futuro)
# Por ahora insertamos 20 posteos aleatorios de los últimos 30 días para probar la arquitectura
sentimientos = ['Positivo', 'Neutral', 'Negativo']
pesos = [0.2, 0.1, 0.7] # Simulamos que hay mayoría de negativos

for _ in range(20):
    dias_restar = random.randint(0, 30)
    fecha_simulada = (datetime.now() - timedelta(days=dias_restar)).strftime('%Y-%m-%d %H:%M:%S')
    sentimiento_simulado = random.choices(sentimientos, weights=pesos)[0]
    cursor.execute("INSERT INTO tweets (tema, date, sentimiento) VALUES (?, ?, ?)", (tema, fecha_simulada, sentimiento_simulado))

conn.commit()
conn.close()
print(f"✅ Extracción completada para el tema: {tema}. Datos guardados en SQLite.")