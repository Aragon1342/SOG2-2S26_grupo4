# PRÁCTICA 1: SISTEMAS ORGANIZACIONALES Y GERENCIALES 2
## Análisis Exploratorio, Segmentación, Modelado Estadístico y Agente Conversacional de IA (Google ADK + FastMCP)
**Universidad de San Carlos de Guatemala — Segundo Semestre 2026**  
**Grupo:** 4 | **Base de Datos:** PostgreSQL en AWS RDS  

---

## 1. DESCRIPCIÓN DEL PROYECTO

Este proyecto implementa una solución integral de analítica de datos e Inteligencia Artificial para una empresa de comercio electrónico en proceso de expansión a tienda física. La plataforma integra:
1. **Infraestructura Cloud:** Base de datos relacional normalizada / dimensional en **AWS RDS (PostgreSQL)**.
2. **Pipeline ETL:** Procesamiento, limpieza y carga estructurada de 6,500 registros transaccionales.
3. **Análisis Estadístico e Inferencia:**
   - **Estudiante 3:** Análisis Exploratorio de Datos (EDA) y Análisis de Tendencias Temporales (Puntos 2 y 3).
   - **Estudiante 4:** Segmentación de Clientes por Cohortes, Género y Fidelización, y Análisis de Correlación e Independencia (Puntos 4 y 5).
4. **Visualizaciones de Alto Impacto:** 14 gráficas profesionales generadas a 300 DPI con justificación metodológica según la tipología de variables (Punto 6).
5. **Servidor FastMCP y Agente Conversacional Google ADK:** Exposición de herramientas analíticas bajo el protocolo estándar MCP para interacción en lenguaje natural con modelos Gemini.
6. **Informes Oficiales en PDF:** Compilados programáticamente con **ReportLab**.

---

## 2. ESTRUCTURA MODULAR DEL REPOSITORIO

```
Practica1/
├── .env                              # Variables de entorno (DATABASE_URL, GEMINI_API_KEY, MODELO)
├── .env.example                      # Plantilla de variables de entorno
├── .gitignore                        # Reglas de exclusión de Git
├── requirements.txt                  # Dependencias de Python
├── README.md                         # Documentación general
│
├── data/                             # Dataset fuente
│   └── Venta_online_c.csv            # Archivo CSV de 6,500 ventas 2021
│
├── sql/                              # Scripts DDL y consultas analíticas SQL
│   ├── schema.sql                    # Esquema relacional, índices y vistas en AWS RDS
│   ├── eda_tendencias.sql            # Consultas de EDA y Tendencias (Estudiante 3)
│   └── segmentacion_correlacion.sql  # Consultas de Segmentación y Correlación (Estudiante 4)
│
├── src/                              # Código fuente principal de análisis y ETL
│   ├── __init__.py
│   ├── etl.py                        # Pipeline ETL hacia AWS RDS PostgreSQL
│   ├── eda_tendencias.py             # Script de análisis EDA y Tendencias
│   └── segmentacion_correlacion.py   # Script de Segmentación y Correlaciones
│
├── mcp_server/                       # Servidor FastMCP modular
│   ├── __init__.py
│   ├── server.py                     # Entrypoint del servidor FastMCP
│   ├── contrato.py                   # Decorador @analisis y clase Resultado
│   ├── db.py                         # Conexión SQLAlchemy a AWS RDS
│   ├── util.py                       # Utilidades de conversión y serialización
│   └── analisis/                     # Módulos de tools autodescubiertas
│       ├── __init__.py
│       ├── eda_tendencias.py         # Tools de EDA y Tendencias
│       └── segmentacion_correlacion.py # Tools de Segmentación y Correlaciones
│
├── agente/                           # Agente Conversacional de IA (Google ADK)
│   ├── __init__.py
│   ├── agent.py                      # Definición de LlmAgent conectado a FastMCP
│   └── graficas.py                   # Manejador de visualizaciones automáticas
│
├── pruebas/                          # Suites de pruebas automatizadas
│   ├── __init__.py
│   ├── pruebas_agente_eda.py         # Validación de tools de Estudiante 3
│   └── pruebas_agente_segmentacion.py# Validación de tools de Estudiante 4
│
├── reportes/                         # Informes técnicos en Markdown y PDFs finales
│   ├── informe_estudiante3_eda_tendencias.md
│   ├── informe_estudiante4_segmentacion_correlacion.md
│   ├── generar_informe_pdf_estudiante3.py
│   ├── generar_informe_pdf_estudiante4.py
│   ├── SOG2-2S26_grupo4_Estudiante3_EDA_Tendencias.pdf
│   └── SOG2-2S26_grupo4_Estudiante4_Segmentacion_Correlacion.pdf
│
├── graficas/                         # 14 Visualizaciones exportadas a 300 DPI
│   ├── graficas_eda/                 # Gráficas 01 a 07 de EDA y Tendencias
│   └── graficas_segmentacion/        # Gráficas 01 a 07 de Segmentación y Correlación
│
└── Enunciado/                        # Enunciado oficial de la práctica
    └── Practica Segundo Semestre 2026.pdf
```

---

## 3. INSTALACIÓN Y CONFIGURACIÓN

### 1. Clonar el Repositorio y Crear Entorno Virtual
```bash
git clone https://github.com/Aragon1342/SOG2-2S26_grupo4.git
cd SOG2-2S26_grupo4/Practica1
python -m venv .venv
# En Windows:
.venv\Scripts\activate
# En Linux/Mac:
source .venv/bin/activate
```

### 2. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar Variables de Entorno (`.env`)
Crear un archivo `.env` en la raíz de `Practica1/` con las siguientes credenciales:
```env
DATABASE_URL=postgresql://<usuario>:<password>@<endpoint-rds-aws>:5432/<nombre_bd>
GEMINI_API_KEY=tu_api_key_de_gemini
MODELO=gemini-2.5-flash
```

---

## 4. COMANDOS DE EJECUCIÓN

### Ejecutar Pipeline ETL (Carga a AWS RDS)
```bash
python src/etl.py
```

### Ejecutar Análisis Estadístico y Generar Gráficas
```bash
# Estudiante 3: EDA y Tendencias
python src/eda_tendencias.py

# Estudiante 4: Segmentación y Correlaciones
python src/segmentacion_correlacion.py
```

### Compilar Informes en PDF (ReportLab)
```bash
# Generar PDF Estudiante 3
python reportes/generar_informe_pdf_estudiante3.py

# Generar PDF Estudiante 4
python reportes/generar_informe_pdf_estudiante4.py
```

### Ejecutar Suites de Pruebas de Herramientas MCP y Agente de IA
```bash
# Pruebas Estudiante 3
python pruebas/pruebas_agente_eda.py

# Pruebas Estudiante 4
python pruebas/pruebas_agente_segmentacion.py
```