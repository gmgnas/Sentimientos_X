@echo off
echo ===================================================
echo Iniciando Arquitectura de Datos: Sentimientos_X
echo ===================================================

:: El comando /d asegura que cambie de disco si es necesario
cd /d "C:\Users\ZOONOSIS NB\Desktop\Sentimientos_X"

echo 1. Sincronizando con la nube...
:: Traemos los cambios que hizo el robot en GitHub para estar al día
git pull origin main

echo 2. Extrayendo datos...
python src/main.py

echo 3. Generando graficos...
python src/visualizacion.py

echo 4. Subiendo a GitHub...
git add .
git commit -m "Update Semanal - Local"

:: Usamos --force para que tu PC tenga la última palabra y no de error
git push origin main --force

echo Proceso finalizado.
timeout /t 5