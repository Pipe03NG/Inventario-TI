"""
seed.py — Poblar la base de datos con datos de prueba.
Ejecutar desde la carpeta backend: python ..\seed.py
"""
import urllib.request, json, sys

BASE = "http://localhost:8000"

def post(endpoint, data):
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    req  = urllib.request.Request(
        BASE + endpoint, data=body,
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        msg = json.loads(e.read()).get("detail", str(e))
        print(f"  SKIP ({msg})")
        return None

# ── Usuarios ──────────────────────────────────────────────────────
usuarios_data = [
    {"nombre": "Carlos Mendoza Ruiz",    "correo": "carlos.mendoza@empresa.com",  "area": "Tecnologia",       "cargo": "Desarrollador Backend"},
    {"nombre": "Laura Gomez Herrera",    "correo": "laura.gomez@empresa.com",     "area": "Diseno",           "cargo": "UX Designer"},
    {"nombre": "Felipe Torres Castillo", "correo": "felipe.torres@empresa.com",   "area": "Finanzas",         "cargo": "Analista Financiero"},
    {"nombre": "Valentina Rios Mora",    "correo": "valentina.rios@empresa.com",  "area": "Recursos Humanos", "cargo": "Coordinadora RRHH"},
    {"nombre": "Andres Salcedo Pinto",   "correo": "andres.salcedo@empresa.com",  "area": "Tecnologia",       "cargo": "DevOps Engineer"},
    {"nombre": "Mariana Ospina Cruz",    "correo": "mariana.ospina@empresa.com",  "area": "Marketing",        "cargo": "Community Manager"},
]

print("=" * 45)
print("  Insertando usuarios")
print("=" * 45)
u_ids = []
for u in usuarios_data:
    r = post("/api/usuarios", u)
    if r:
        u_ids.append(r["id"])
        print(f"  [OK] [{r['id']}] {r['nombre']}")

# ── Equipos ───────────────────────────────────────────────────────
equipos_data = [
    {"tipo": "Laptop",  "marca": "Dell",    "modelo": "Latitude 5530",    "numero_serie": "SN-DL-001", "estado": "Nuevo"},
    {"tipo": "Laptop",  "marca": "HP",      "modelo": "EliteBook 840 G9", "numero_serie": "SN-HP-002", "estado": "Nuevo"},
    {"tipo": "Laptop",  "marca": "Lenovo",  "modelo": "ThinkPad T14",     "numero_serie": "SN-LN-003", "estado": "Usado"},
    {"tipo": "Desktop", "marca": "Dell",    "modelo": "OptiPlex 7090",    "numero_serie": "SN-DL-004", "estado": "Nuevo"},
    {"tipo": "Desktop", "marca": "HP",      "modelo": "ProDesk 600 G6",   "numero_serie": "SN-HP-005", "estado": "Usado"},
    {"tipo": "Monitor", "marca": "LG",      "modelo": "27UL500 4K",       "numero_serie": "SN-LG-006", "estado": "Nuevo"},
    {"tipo": "Monitor", "marca": "Samsung", "modelo": "S27A600NWU",       "numero_serie": "SN-SM-007", "estado": "Nuevo"},
    {"tipo": "Laptop",  "marca": "Apple",   "modelo": "MacBook Pro M3",   "numero_serie": "SN-AP-008", "estado": "Nuevo"},
]

print("\n" + "=" * 45)
print("  Insertando equipos")
print("=" * 45)
e_ids = []
for e in equipos_data:
    r = post("/api/equipos", e)
    if r:
        e_ids.append(r["id"])
        print(f"  [OK] [{r['id']}] {r['tipo']} {r['marca']} {r['modelo']}")

# ── Asignaciones (cada usuario recibe un equipo) ──────────────────
print("\n" + "=" * 45)
print("  Creando asignaciones")
print("=" * 45)
pares = list(zip(u_ids, e_ids))   # 6 usuarios, 8 equipos -> 6 asignaciones
for uid, eid in pares:
    r = post("/api/asignaciones", {"equipo_id": eid, "usuario_id": uid})
    if r:
        print(f"  [OK] Asignacion #{r['id']} — equipo {eid} -> usuario {uid}")

print("\n  2 equipos quedan disponibles (sin asignar)")
print("\nDone! Abre http://localhost:8000 para verlos.")
