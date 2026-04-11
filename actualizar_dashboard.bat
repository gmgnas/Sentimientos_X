@echo off
echo ===================================================
echo Iniciando Arquitectura de Datos: Sentimientos_X
echo ===================================================

cd "C:\Users\ZOONOSIS NB\Desktop\Sentimientos_X"

echo 1. Extrayendo datos...
python src/main.py

echo 2. Generando graficos...
python src/visualizacion.py

echo 3. Subiendo a GitHub...
git add .
git commit -m "Update Semanal"
git push origin main

echo Proceso finalizado.
timeout /t 5