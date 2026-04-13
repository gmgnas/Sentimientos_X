import sqlite3
import yaml
import os
import tweepy
import pandas as pd
from datetime import datetime

# 1. Rutas
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(base_dir, 'data', 'sentimientos.db')
config_path = os.path.join(base_dir, 'src', 'config.yaml')

# 2. Leer Token desde Variable de Entorno y Configuración
bearer_token = os.getenv('X_BEARER_TOKEN')

with open(config_path, 'r', encoding='utf-8') as file:
    config = yaml.safe_load(file)

tema = config['analisis']['query']

# 3. Conectar y REINICIAR Base de Datos
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Limpieza total: Borramos la tabla para que no se acumulen datos viejos
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

# 4. Extracción con Tweepy (API v2)
client = tweepy.Client(bearer_token=bearer_token)

print(f"Buscando posts reales sobre: {tema}...")

try:
    # Buscamos 100 tweets recientes del tema elegido
    tweets = client.search_recent_tweets(query=f"{tema} -is:retweet lang:es", 
                                        tweet_fields=['created_at'], 
                                        max_results=1000)
    
    lista_tweets = []
    sentimientos_posibles = ['Positivo', 'Neutral', 'Negativo']

    if tweets.data:
        for tweet in tweets.data:
            lista_tweets.append({
                'tema': tema,
                'date': tweet.created_at.strftime('%Y-%m-%d'),
                'sentimiento': random.choice(sentimientos_posibles) # Aquí va tu lógica de análisis real
            })
        
        # Guardar en SQL usando Pandas (Modo replace para doble seguridad)
        df = pd.DataFrame(lista_tweets)
        df.to_sql('tweets', conn, if_exists='replace', index=False)
        print(f"✅ Se guardaron {len(df)} posts nuevos sobre {tema}.")
    else:
        print("❌ No se encontraron tweets nuevos.")

except Exception as e:
    print(f"❌ Error API: {e}")

finally:
    conn.close()