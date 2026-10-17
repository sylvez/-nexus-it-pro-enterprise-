import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector

try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

app = FastAPI(title="NexusIT Pro Enterprise API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de tu Base de Datos MySQL local
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "202502241",  # <--- COLOCA AQUÍ TU CONTRASEÑA DE MYSQL
    "database": "nexus_it_enterprise"
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

class NuevoTicket(BaseModel):
    titulo: str
    descripcion: str
    solicitante: str
    prioridad: str

class CambioEstado(BaseModel):
    estado: str

class NuevoActivo(BaseModel):
    codigo_patrimonial: str
    equipo: str
    ubicacion: str
    estado: str = "Operativo"

def generar_diagnostico_inteligente(titulo: str, descripcion: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY", "")
    if GEMINI_AVAILABLE and api_key:
        try:
            client = genai.Client(api_key=api_key)
            prompt = (
                f"Actúa como un Ingeniero de Soporte TI Senior. Dame exactamente 3 pasos técnicos, "
                f"breves y directos para resolver este ticket:\nTítulo: {titulo}\nDetalle: {descripcion}"
            )
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text.strip()
        except Exception:
            pass

    texto = (titulo + " " + descripcion).lower()
    if "red" in texto or "wifi" in texto or "internet" in texto or "ip" in texto:
        return "1. Verificar enlace físico/VLAN y hacer ping al Gateway.\n2. Renovar concesión DHCP (ipconfig /release & /renew) y limpiar caché DNS.\n3. Revisar estado de los nodos Mesh y saturación de canal."
    elif "base de datos" in texto or "mysql" in texto or "sql" in texto or "3306" in texto:
        return "1. Comprobar estado del demonio mysqld en el servidor.\n2. Auditar tablas de privilegios y bind-address en my.cnf.\n3. Revisar logs de transacciones lentas o bloqueos de tabla."
    elif "impresora" in texto or "imprimir" in texto:
        return "1. Reiniciar el servicio Print Spooler en el equipo cliente.\n2. Verificar que el puerto TCP/IP apunte a una IP fija reservada.\n3. Comprobar niveles de tinta y estado de cabezales."
    else:
        return "1. Reproducir el incidente en entorno controlado y capturar visor de eventos.\n2. Verificar integridad de archivos del sistema y consumo de RAM/CPU.\n3. Escalar a Nivel 2 documentando cambios en bitácora."

@app.get("/api/dashboard")
def obtener_dashboard():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM tickets ORDER BY id DESC")
    tickets = cursor.fetchall()

    cursor.execute("SELECT * FROM activos_ti ORDER BY id DESC")
    activos = cursor.fetchall()

    cursor.execute("SELECT * FROM bitacora_auditoria ORDER BY id DESC LIMIT 25")
    bitacora = cursor.fetchall()

    cursor.close()
    conn.close()

    resumen = {
        "total": len(tickets),
        "abiertos": sum(1 for t in tickets if t["estado"] == "Abierto"),
        "en_proceso": sum(1 for t in tickets if t["estado"] == "En Proceso"),
        "resueltos": sum(1 for t in tickets if t["estado"] == "Resuelto"),
        "criticos": sum(1 for t in tickets if t["prioridad"] == "Crítica"),
        "total_activos": len(activos)
    }

    return {
        "metricas": resumen,
        "tickets": tickets,
        "activos": activos,
        "bitacora": bitacora
    }

@app.post("/api/tickets")
def crear_ticket(ticket: NuevoTicket):
    diagnostico = generar_diagnostico_inteligente(ticket.titulo, ticket.descripcion)
    conn = get_db()
    cursor = conn.cursor()
    sql = """
        INSERT INTO tickets (titulo, descripcion, solicitante, prioridad, diagnostico_ia)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (ticket.titulo, ticket.descripcion, ticket.solicitante, ticket.prioridad, diagnostico))
    conn.commit()
    nuevo_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return {"mensaje": "Ticket creado con éxito", "id": nuevo_id, "diagnostico_ia": diagnostico}

@app.put("/api/tickets/{ticket_id}/estado")
def actualizar_estado_ticket(ticket_id: int, datos: CambioEstado):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE tickets SET estado = %s WHERE id = %s", (datos.estado, ticket_id))
    conn.commit()
    cursor.close()
    conn.close()
    return {"mensaje": "Estado actualizado y auditado por Trigger en MySQL"}

@app.post("/api/activos")
def crear_activo(activo: NuevoActivo):
    conn = get_db()
    cursor = conn.cursor()
    try:
        sql = """
            INSERT INTO activos_ti (codigo_patrimonial, equipo, ubicacion, estado)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, (activo.codigo_patrimonial.upper().strip(), activo.equipo, activo.ubicacion, activo.estado))
        conn.commit()
        nuevo_id = cursor.lastrowid
        return {"mensaje": "Activo registrado con éxito", "id": nuevo_id}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=400, detail=f"Error al registrar activo: {err.msg}")
    finally:
        cursor.close()
        conn.close()

@app.put("/api/activos/{activo_id}/estado")
def actualizar_estado_activo(activo_id: int, datos: CambioEstado):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE activos_ti SET estado = %s WHERE id = %s", (datos.estado, activo_id))
    conn.commit()
    cursor.close()
    conn.close()
    return {"mensaje": "Estado de activo actualizado y auditado"}