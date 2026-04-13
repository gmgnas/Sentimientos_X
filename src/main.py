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

# 3. Conectar y Configurar Base de Datos (Persistente)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# IMPORTANTE: Ya no hacemos DROP TABLE. Creamos la tabla si no existe.
# Agregamos 'tweet_id' como UNIQUE para no guardar dos veces el mismo post.
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

# 4. Extracción con Tweepy
if not bearer_token:
    print("❌ ERROR: No se detectó el Token en las variables de entorno.")
else:
    try:
        client = tweepy.Client(bearer_token=bearer_token)
        print(f"Buscando posts sobre: {tema}...")
        
        # Buscamos los 100 más recientes
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
                    'date': tweet.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'sentimiento': random.choice(sentimientos_posibles),
                    'tweet_id': str(tweet.id) # Guardamos el ID real para evitar duplicados
                })
            
            # Convertimos a DataFrame
            df_nuevos = pd.DataFrame(lista_tweets)
            
            # Guardamos los datos nuevos. 
            # Usamos un bucle para insertar uno por uno y que el 'UNIQUE' ignore los repetidos.
            exitos = 0
            for _, row in df_nuevos.iterrows():
                try:
                    row.to_frame().T.to_sql('tweets', conn, if_exists='append', index=False)
                    exitos += 1
                except:
                    # Si el tweet_id ya existe, salta aquí y no hace nada (evita duplicados)
                    continue
            
            print(f"✅ ¡Proceso completado! Se agregaron {exitos} posts nuevos sobre {tema}.")
            
            # Verificación de cuántos días hay en total
            cursor.execute("SELECT COUNT(DISTINCT date(date)) FROM tweets")
            dias_acumulados = cursor.fetchone()[0]
            print(f"📈 Tu base de datos ahora tiene historial de {dias_acumulados} días distintos.")

        else:
            print("❓ La API no devolvió nada nuevo.")

    except Exception as e:
        print(f"❌ Error de API: {e}")

conn.close()