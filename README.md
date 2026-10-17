# 🛡️ NexusIT Pro | Enterprise ITSM, Asset Management & AI Auditing

Sistema empresarial Full-Stack para la gestión de tickets de soporte técnico (Helpdesk), control de inventario de activos de hardware y auditoría forense automatizada a nivel de motor de base de datos.

## 🚀 Características de Nivel Empresarial
* **Diagnóstico Técnico con IA (Gemini API + Fallback Engine):** Genera planes de resolución de 3 pasos al instante según la descripción del incidente.
* **Auditoría Forense Inmutable (MySQL Triggers):** Cada creación o cambio de estado en los tickets dispara automáticamente un `TRIGGER` en MySQL (`AFTER INSERT` / `AFTER UPDATE`) que registra el cambio en una tabla de bitácora sin depender del código del backend.
* **Dashboard Operativo en Tiempo Real:** Visualización de KPIs, métricas de SLA y gráficas dinámicas con Chart.js y Tailwind CSS en modo oscuro.
* **Modo Simulación (1-Click Demo):** Permite a reclutadores y clientes probar el flujo completo en un clic.

## 🛠️ Stack Tecnológico
* **Backend:** Python 3.12, FastAPI, Uvicorn, Pydantic
* **Base de Datos:** MySQL 8.0 (InnoDB, Triggers, Foreign Keys)
* **Inteligencia Artificial:** Google Gemini 2.5 Flash SDK
* **Frontend:** HTML5, JavaScript (ES6+), Tailwind CSS, Chart.js

## ⚙️ Instalación Rápida
1. Ejecutar el script `database.sql` en MySQL Server.
2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt