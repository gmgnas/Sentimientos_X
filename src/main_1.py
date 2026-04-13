import sqlite3
import yaml
import os
import tweepy
import pandas as pd
import random
from datetime import datetime

# 1. Rutas
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(base_dir, 'data', 'sentimientos1.db')
config_path = os.path.join(base_dir, 'src', 'config.yaml')

# 2. Leer Token y Configuración
bearer_token = os.getenv('X_BEARER_TOKEN')

with open(config_path, 'r', encoding='utf-8') as file:
    config = yaml.safe_load(file)

# IMPORTANTE: Asegúrate de que en tu config.yaml, el 'query' sea una URL (ej: google.com)
url_objetivo = config['analisis']['query']

# 3. Conectar y Configurar Base de Datos
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS tweets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tema TEXT,
        date TEXT,
        sentimiento TEXT,
        tweet_id TEXT UNIQUE
    )
''')
conn.commit()

# 4. Extracción basada en URL
if not bearer_token:
    print("❌ ERROR: No se detectó el Token en las variables de entorno.")
else:
    try:
        client = tweepy.Client(bearer_token=bearer_token)
        
        # Construimos el query especializado para URLs
        # El operador 'url:' busca posts que contengan el enlace específico
        query_url = f'url:"{url_objetivo}" -is:retweet'
        
        print(f"Buscando posts que comparten la URL: {url_objetivo}...")
        
        tweets = client.search_recent_tweets(
            query=query_url, 
            tweet_fields=['created_at', 'entities'], 
            max_results=100
        )
        
        lista_tweets = []
        sentimientos_posibles = ['Positivo', 'Neutral', 'Negativo']

        if tweets.data:
            for tweet in tweets.data:
                lista_tweets.append({
                    'tema': url_objetivo, # Guardamos la URL como identificador
                    'date': tweet.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'sentimiento': random.choice(sentimientos_posibles),
                    'tweet_id': str(tweet.id) 
                })
            
            df_nuevos = pd.DataFrame(lista_tweets)
            
            exitos = 0
            for _, row in df_nuevos.iterrows():
                try:
                    # Usamos INSERT OR IGNORE para manejar el UNIQUE tweet_id
                    cursor.execute("""
                        INSERT OR IGNORE INTO tweets (tema, date, sentimiento, tweet_id) 
                        VALUES (?, ?, ?, ?)
                    """, (row['tema'], row['date'], row['sentimiento'], row['tweet_id']))
                    exitos += 1
                except Exception as e:
                    continue
            
            conn.commit()
            print(f"✅ ¡Proceso completado! Se rastrearon {exitos} posts nuevos vinculados a la URL.")
            
            cursor.execute("SELECT COUNT(DISTINCT substr(date, 1, 10)) FROM tweets WHERE tema = ?", (url_objetivo,))
            dias_acumulados = cursor.fetchone()[0]
            print(f"📈 Historial acumulado para esta URL: {dias_acumulados} días.")

        else:
            print(f"❓ No se encontraron posts recientes que mencionen la URL: {url_objetivo}")

    except Exception as e:
        print(f"❌ Error de API: {e}")

conn.close()