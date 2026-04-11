# Arquitectura de Soluciones - TP 01

## Análisis de Sentimientos en X

**Alumnos:** Facundo Zubeldia - Gonzalo Martín González Nastovich

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