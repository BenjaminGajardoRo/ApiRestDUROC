from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import List, Optional, Dict

app = FastAPI()

# --- USUARIOS PA PROBAR ---
usuarios = {
    "admin": {"password": "admin", "rol": "Administrador"},
    "reflauta": {"password": "trompeta", "rol": "Orquestador"},
    "notch": {"password": "creeper", "rol": "Usuario"},
}

servicios = []
reglas_orquestacion = {}
tokens_validos = {
    "token_admin": "Administrador",
    "token_orq": "Orquestador",
    "token_user": "Usuario"
}

class Servicio(BaseModel):
    id: int
    nombre: str
    descripcion: str
    endpoints: List[str]

class OrquestacionRequest(BaseModel):
    servicio_destino: str
    parametros_adicionales: Optional[Dict] = {}

class ReglasOrquestacion(BaseModel):
    reglas: Dict

class AuthRequest(BaseModel):
    nombre_usuario: str
    contrasena: str

class AutorizarAccesoRequest(BaseModel):
    recursos: List[str]
    rol_usuario: str

# --- Aqui se busca el token ---
def get_rol(token: str = Header(...)):
    if token not in tokens_validos:
        raise HTTPException(status_code=401, detail="Token inválido")
    return tokens_validos[token]

# --- Endpoints ---

@app.post("/orquestar")
def orquestar(data: OrquestacionRequest, rol: str = Depends(get_rol)):
    if rol not in ["Orquestador", "Administrador"]:
        raise HTTPException(status_code=403, detail="No autorizado para orquestar")
    return {
        "mensaje": "Orquestación iniciada",
        "servicio": data.servicio_destino,
        "parametros": data.parametros_adicionales
    }

@app.get("/informacion-servicio/{id}")
def obtener_info(id: int, rol: str = Depends(get_rol)):
    for s in servicios:
        if s["id"] == id:
            return s
    raise HTTPException(status_code=404, detail="Servicio no encontrado")

@app.post("/registrar-servicio")
def registrar_servicio(servicio: Servicio, rol: str = Depends(get_rol)):
    if rol != "Administrador":
        raise HTTPException(status_code=403, detail="No autorizado para registrar")
    servicios.append(servicio.dict())
    return {"mensaje": "Servicio registrado", "servicio": servicio}

@app.put("/actualizar-reglas-orquestacion")
def actualizar_reglas(data: ReglasOrquestacion, rol: str = Depends(get_rol)):
    if rol != "Orquestador":
        raise HTTPException(status_code=403, detail="No autorizado para actualizar reglas")
    reglas_orquestacion.update(data.reglas)
    return {"mensaje": "Reglas actualizadas", "reglas": reglas_orquestacion}

@app.post("/autenticar-usuario")
def autenticar(data: AuthRequest):
    user = usuarios.get(data.nombre_usuario)
    if not user or user["password"] != data.contrasena:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    # Simula token
    for token, rol in tokens_validos.items():
        if rol == user["rol"]:
            return {"token": token, "rol": rol}
    raise HTTPException(status_code=500, detail="No se pudo asignar token")

@app.post("/autorizar-acceso")
def autorizar(data: AutorizarAccesoRequest, rol: str = Depends(get_rol)):
    if rol != data.rol_usuario:
        raise HTTPException(status_code=403, detail="Acceso denegado por rol")
    return {"mensaje": "Acceso autorizado", "recursos": data.recursos}
