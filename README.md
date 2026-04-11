[🔗 Clic aquí para ver el Dashboard en vivo](https://gmgnas.github.io/Sentimientos_X/)

# Analisis de Sentimientos de X

**Materia:** Arquitectura de Soluciones

**Alumnos:** Facundo Zubeldia - Gonzalo Martín González Nastovich

## 1. Objetivo del Proyecto
Desarrollar un flujo de datos (Pipeline) automático para monitorear la percepción pública en la red X, con un historial móvil de 30 días y actualizaciones semanales, cumpliendo con la normativa legal argentina.

## 2.Componentes de la Arquitectura:
   
   * Ingesta: Script Python utilizando la API v2 de X.
   
   * Procesamiento: Clasificación de sentimientos (Positivo, Neutro, Negativo) mediante modelos de NLP.
   
   * Persistencia: Base de datos relacional SQLite para evitar duplicados y mantener integridad.
   
   * Visualización: Dashboard interactivo basado en Plotly, desplegado en infraestructura de GitHub Pages.

##  Arquitectura de la Solución
```mermaid
flowchart TD
    %% Nodos Externos
    U["👤 Usuario/Config"]
    API["🌐 API de X (v2)"]
    ML["🧠 Modelo NLP"]
    DB[("🗄️ Base de Datos")]
    D["📊 Dashboard"]

    %% Proceso Principal (Script)
    subgraph S ["🐍 Script Python (Orquestador)"]
        direction TB
        P["⚙️ Config: Tema y Fechas\n(Inicial 1 mes / Semanal 7d)"]
        E["📥 Extractor API v2"]
        C["🧹 Limpieza y Anonimización\n(Ley 25.326)"]
        A["🎭 Análisis de Sentimiento"]
    end

    %% Flujo de datos
    U --> P
    P --> E
    E <--> API
    E --> C
    C --> A
    A <--> ML
    A -->|"Carga Incremental"| DB
    DB --> D

    %% Estilos
    classDef input fill:#add8e6,stroke:#333,stroke-width:2px
    classDef process fill:#90ee90,stroke:#333,stroke-width:2px
    classDef external fill:#ffff00,stroke:#333,stroke-width:2px
    classDef analysis fill:#ffa500,stroke:#333,stroke-width:2px
    classDef storage fill:#d3d3d3,stroke:#333,stroke-width:2px
    classDef output fill:#dda0dd,stroke:#333,stroke-width:2px

    class U input
    class P,E,C,A process
    class API external
    class ML analysis
    class DB storage
    class D output
```
## 3. Automatización
Se implementó un desacoplamiento mediante config.yaml, permitiendo la reusabilidad del código. La ejecución se gestiona mediante un archivo de procesamiento por lotes (.bat) integrable al programador de tareas del sistema operativo.

## 4. Marco Legal
La solución garantiza la privacidad mediante:

   * Disociación de datos (eliminación de nombres reales).

   * Almacenamiento exclusivo de metadatos de opinión.

   * Cumplimiento de la finalidad estadística solicitada por el cliente.
