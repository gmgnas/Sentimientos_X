import sqlite3
import yaml
import os
import tweepy
import random
from datetime import datetime

# 1. Rutas
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(base_dir, 'data', 'sentimientos.db')
config_path = os.path.join(base_dir, 'src', 'config.yaml')

# 2. Leer Configuración y Token
bearer_token = os.getenv('X_BEARER_TOKEN')

with open(config_path, 'r', encoding='utf-8') as file:
    config = yaml.safe_load(file)

tema = config['analisis']['query']

# 3. Conectar a Base de Datos
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

# 4. Ingesta desde la API de X
print(f"Buscando posts reales sobre: {tema}...")
try:
    client = tweepy.Client(bearer_token=bearer_token)
    query_busqueda = f"{tema} -is:retweet lang:es"
    tweets = client.search_recent_tweets(query=query_busqueda, max_results=10, tweet_fields=['created_at'])

    if tweets.data:
        sentimientos_lista = ['Positivo', 'Neutral', 'Negativo']
        for tweet in tweets.data:
            fecha = tweet.created_at.strftime('%Y-%m-%d %H:%M:%S')
            # Simulamos análisis de sentimiento sobre el texto real
            sent_simulado = random.choices(sentimientos_lista, weights=[0.3, 0.4, 0.3])[0]
            
            cursor.execute("INSERT INTO tweets (tema, date, sentimiento) VALUES (?, ?, ?)", 
                           (tema, fecha, sent_simulado))
        print(f"✅ Se ingestaron {len(tweets.data)} posts de X.")
    else:
        print("No se encontraron resultados recientes.")

except Exception as e:
    print(f"❌ Error API: {e}")

conn.commit()
conn.close()