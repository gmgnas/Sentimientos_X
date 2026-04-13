import sqlite3
import yaml
import os
import tweepy
import pandas as pd
import random
from datetime import datetime

# 1. Rutas
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(base_dir, 'data', 'sentimientos.db')
config_path = os.path.join(base_dir, 'src', 'config.yaml')

# 2. Leer Token y Configuración
bearer_token = os.getenv('X_BEARER_TOKEN')

with open(config_path, 'r', encoding='utf-8') as file:
    config = yaml.safe_load(file)

tema = config['analisis']['query']

# 3. Conectar y Reiniciar Base de Datos
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('DROP TABLE IF EXISTS tweets')
cursor.execute('''
    CREATE TABLE tweets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tema TEXT,
        date TEXT,
        sentimiento TEXT
    )
''')
conn.commit()

# 4. Extracción con Tweepy
if not bearer_token:
    print("❌ ERROR: No se detectó el Token en las variables de entorno.")
else:
    try:
        client = tweepy.Client(bearer_token=bearer_token)
        print(f"Buscando posts sobre: {tema}...")
        
        # Subimos a 100 resultados (Máximo del plan gratuito)
        tweets = client.search_recent_tweets(
            query=f"{tema} -is:retweet", 
            tweet_fields=['created_at'], 
            max_results=100
        )
        
        lista_tweets = []
        sentimientos_posibles = ['Positivo', 'Neutral', 'Negativo']

        if tweets.data:
            for tweet in tweets.data:
                lista_tweets.append({
                    'tema': tema,
                    # Guardamos la fecha completa, la limpiaremos en la visualización
                    'date': tweet.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'sentimiento': random.choice(sentimientos_posibles)
                })
            
            df = pd.DataFrame(lista_tweets)
            df.to_sql('tweets', conn, if_exists='replace', index=False)
            print(f"✅ ¡Éxito! Se guardaron {len(df)} posts sobre {tema}.")
        else:
            print("❓ La API no devolvió nada.")

    except Exception as e:
        print(f"❌ Error de API: {e}")

conn.close()