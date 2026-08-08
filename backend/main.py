from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List
from datetime import datetime, timezone
import os

import models
import schemas
from database import engine, get_db

# ─── Crear tablas al iniciar ─────────────────────────────────────────────────
models.Base.metadata.create_all(bind=engine)

# ─── App FastAPI ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="Sistema de Inventario TI",
    description="API para gestión de equipos de cómputo y asignación de activos",
    version="1.0.0",
)

# ─── Servir archivos estáticos del frontend ───────────────────────────────────
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(FRONTEND_DIR, "static")),
    name="static",
)


# ─── Rutas del Frontend (sirve los HTML) ─────────────────────────────────────

@app.get("/", response_class=FileResponse, include_in_schema=False)
def root():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/usuarios-page", response_class=FileResponse, include_in_schema=False)
def page_usuarios():
    return FileResponse(os.path.join(FRONTEND_DIR, "usuarios.html"))

@app.get("/equipos-page", response_class=FileResponse, include_in_schema=False)
def page_equipos():
    return FileResponse(os.path.join(FRONTEND_DIR, "equipos.html"))

@app.get("/actas-page", response_class=FileResponse, include_in_schema=False)
def page_actas():
    return FileResponse(os.path.join(FRONTEND_DIR, "actas.html"))


# ══════════════════════════════════════════════════════════════════════════════
#  API — USUARIOS
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/api/usuarios", response_model=List[schemas.UsuarioOut], tags=["Usuarios"])
def listar_usuarios(db: Session = Depends(get_db)):
    """Retorna todos los usuarios registrados."""
    return db.query(models.Usuario).order_by(models.Usuario.id.desc()).all()


@app.get("/api/usuarios/{usuario_id}", response_model=schemas.UsuarioOut, tags=["Usuarios"])
def obtener_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@app.post("/api/usuarios", response_model=schemas.UsuarioOut, status_code=status.HTTP_201_CREATED, tags=["Usuarios"])
def crear_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    """Registra un nuevo usuario/colaborador."""
    # Verificar correo duplicado
    existente = db.query(models.Usuario).filter(models.Usuario.correo == usuario.correo).first()
    if existente:
        raise HTTPException(status_code=400, detail="Ya existe un usuario con ese correo electrónico")

    nuevo = models.Usuario(**usuario.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@app.put("/api/usuarios/{usuario_id}", response_model=schemas.UsuarioOut, tags=["Usuarios"])
def actualizar_usuario(usuario_id: int, datos: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Verificar correo duplicado en otro usuario
    duplicado = db.query(models.Usuario).filter(
        models.Usuario.correo == datos.correo,
        models.Usuario.id != usuario_id
    ).first()
    if duplicado:
        raise HTTPException(status_code=400, detail="Ese correo ya está en uso por otro usuario")

    for campo, valor in datos.model_dump().items():
        setattr(usuario, campo, valor)

    db.commit()
    db.refresh(usuario)
    return usuario


@app.delete("/api/usuarios/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Usuarios"])
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Verificar que no tenga equipos asignados actualmente
    asignacion_activa = db.query(models.Asignacion).filter(
        models.Asignacion.usuario_id == usuario_id,
        models.Asignacion.activa == 1
    ).first()
    if asignacion_activa:
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar un usuario con equipos asignados. Primero desasigne sus equipos."
        )

    db.delete(usuario)
    db.commit()


# ══════════════════════════════════════════════════════════════════════════════
#  API — EQUIPOS
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/api/equipos", response_model=List[schemas.EquipoOut], tags=["Equipos"])
def listar_equipos(db: Session = Depends(get_db)):
    """Retorna todos los equipos en inventario."""
    return db.query(models.Equipo).order_by(models.Equipo.id.desc()).all()


@app.get("/api/equipos/{equipo_id}", response_model=schemas.EquipoOut, tags=["Equipos"])
def obtener_equipo(equipo_id: int, db: Session = Depends(get_db)):
    equipo = db.query(models.Equipo).filter(models.Equipo.id == equipo_id).first()
    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    return equipo


@app.post("/api/equipos", response_model=schemas.EquipoOut, status_code=status.HTTP_201_CREATED, tags=["Equipos"])
def crear_equipo(equipo: schemas.EquipoCreate, db: Session = Depends(get_db)):
    """Registra un nuevo equipo en el inventario."""
    existente = db.query(models.Equipo).filter(models.Equipo.numero_serie == equipo.numero_serie).first()
    if existente:
        raise HTTPException(status_code=400, detail="Ya existe un equipo con ese número de serie")

    nuevo = models.Equipo(**equipo.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@app.put("/api/equipos/{equipo_id}", response_model=schemas.EquipoOut, tags=["Equipos"])
def actualizar_equipo(equipo_id: int, datos: schemas.EquipoCreate, db: Session = Depends(get_db)):
    equipo = db.query(models.Equipo).filter(models.Equipo.id == equipo_id).first()
    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")

    duplicado = db.query(models.Equipo).filter(
        models.Equipo.numero_serie == datos.numero_serie,
        models.Equipo.id != equipo_id
    ).first()
    if duplicado:
        raise HTTPException(status_code=400, detail="Ese número de serie ya está en uso")

    for campo, valor in datos.model_dump().items():
        setattr(equipo, campo, valor)

    db.commit()
    db.refresh(equipo)
    return equipo


@app.delete("/api/equipos/{equipo_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Equipos"])
def eliminar_equipo(equipo_id: int, db: Session = Depends(get_db)):
    equipo = db.query(models.Equipo).filter(models.Equipo.id == equipo_id).first()
    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")

    asignacion_activa = db.query(models.Asignacion).filter(
        models.Asignacion.equipo_id == equipo_id,
        models.Asignacion.activa == 1
    ).first()
    if asignacion_activa:
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar un equipo que está asignado. Primero desasígnelo."
        )

    db.delete(equipo)
    db.commit()


# ══════════════════════════════════════════════════════════════════════════════
#  API — INVENTARIO (Dashboard)
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/api/inventario", response_model=List[schemas.InventarioItem], tags=["Inventario"])
def ver_inventario(db: Session = Depends(get_db)):
    """
    Retorna todos los equipos con su estado de asignación.
    Muestra si están Disponibles o Asignados (con datos del usuario).
    """
    equipos = db.query(models.Equipo).order_by(models.Equipo.id.desc()).all()
    resultado = []

    for equipo in equipos:
        asignacion_activa = db.query(models.Asignacion).filter(
            models.Asignacion.equipo_id == equipo.id,
            models.Asignacion.activa == 1
        ).first()

        item = schemas.InventarioItem(
            equipo=schemas.EquipoOut.model_validate(equipo),
            disponible=asignacion_activa is None,
            asignado_a=schemas.UsuarioOut.model_validate(asignacion_activa.usuario) if asignacion_activa else None,
            asignacion_id=asignacion_activa.id if asignacion_activa else None,
        )
        resultado.append(item)

    return resultado


@app.get("/api/inventario/stats", tags=["Inventario"])
def estadisticas(db: Session = Depends(get_db)):
    """Retorna contadores rápidos para el dashboard."""
    total_equipos = db.query(models.Equipo).count()
    total_usuarios = db.query(models.Usuario).count()
    asignados = db.query(models.Asignacion).filter(models.Asignacion.activa == 1).count()
    disponibles = total_equipos - asignados

    return {
        "total_equipos": total_equipos,
        "total_usuarios": total_usuarios,
        "equipos_asignados": asignados,
        "equipos_disponibles": disponibles,
    }


# ══════════════════════════════════════════════════════════════════════════════
#  API — ASIGNACIONES
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/api/asignaciones", response_model=schemas.AsignacionOut, status_code=status.HTTP_201_CREATED, tags=["Asignaciones"])
def asignar_equipo(datos: schemas.AsignacionCreate, db: Session = Depends(get_db)):
    """Asigna un equipo disponible a un usuario."""
    # Verificar que el equipo existe
    equipo = db.query(models.Equipo).filter(models.Equipo.id == datos.equipo_id).first()
    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")

    # Verificar que el usuario existe
    usuario = db.query(models.Usuario).filter(models.Usuario.id == datos.usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Verificar que el equipo no esté ya asignado
    ya_asignado = db.query(models.Asignacion).filter(
        models.Asignacion.equipo_id == datos.equipo_id,
        models.Asignacion.activa == 1
    ).first()
    if ya_asignado:
        raise HTTPException(status_code=400, detail="El equipo ya está asignado a otro usuario")

    nueva = models.Asignacion(
        equipo_id=datos.equipo_id,
        usuario_id=datos.usuario_id,
        activa=1,
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva


@app.patch("/api/asignaciones/{asignacion_id}/devolver", response_model=schemas.AsignacionOut, tags=["Asignaciones"])
def devolver_equipo(asignacion_id: int, db: Session = Depends(get_db)):
    """Desasigna / libera un equipo (marca la asignación como inactiva)."""
    asignacion = db.query(models.Asignacion).filter(
        models.Asignacion.id == asignacion_id,
        models.Asignacion.activa == 1
    ).first()

    if not asignacion:
        raise HTTPException(status_code=404, detail="Asignación activa no encontrada")

    asignacion.activa = 0
    asignacion.fecha_devolucion = datetime.now(timezone.utc)
    db.commit()
    db.refresh(asignacion)
    return asignacion


@app.get("/api/asignaciones", response_model=List[schemas.AsignacionOut], tags=["Asignaciones"])
def listar_asignaciones(solo_activas: bool = True, db: Session = Depends(get_db)):
    """Lista todas las asignaciones. Por defecto solo las activas."""
    query = db.query(models.Asignacion)
    if solo_activas:
        query = query.filter(models.Asignacion.activa == 1)
    return query.order_by(models.Asignacion.id.desc()).all()
