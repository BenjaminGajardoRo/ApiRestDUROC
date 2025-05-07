from fastapi import FastAPI, HTTPException, Depends, Header

app = FastAPI()

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


def get_rol(token: str = Header(...)):
    if token not in tokens_validos:
        raise HTTPException(status_code=401, detail="Token inválido")
    return tokens_validos[token]


@app.post("/orquestar")
def orquestar(data: dict, rol: str = Depends(get_rol)):
    if rol not in ["Orquestador", "Administrador"]:
        raise HTTPException(status_code=403, detail="No autorizado para orquestar")
    return {
        "mensaje": "Orquestación iniciada",
        "servicio": data.get("servicio_destino"),
        "parametros": data.get("parametros_adicionales", {})
    }

@app.get("/informacion-servicio/{id}")
def obtener_info(id: int, rol: str = Depends(get_rol)):
    for s in servicios:
        if s["id"] == id:
            return s
    raise HTTPException(status_code=404, detail="Servicio no encontrado")

@app.post("/registrar-servicio")
def registrar_servicio(servicio: dict, rol: str = Depends(get_rol)):
    if rol != "Administrador":
        raise HTTPException(status_code=403, detail="No autorizado para registrar")
    servicios.append(servicio)
    return {"mensaje": "Servicio registrado", "servicio": servicio}

@app.put("/actualizar-reglas-orquestacion")
def actualizar_reglas(data: dict, rol: str = Depends(get_rol)):
    if rol != "Orquestador":
        raise HTTPException(status_code=403, detail="No autorizado para actualizar reglas")
    reglas_orquestacion.update(data)
    return {"mensaje": "Reglas actualizadas", "reglas": reglas_orquestacion}

@app.post("/autenticar-usuario")
def autenticar(data: dict):
    user = usuarios.get(data.get("nombre_usuario"))
    if not user or user["password"] != data.get("contrasena"):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    for token, rol in tokens_validos.items():
        if rol == user["rol"]:
            return {"token": token, "rol": rol}
    raise HTTPException(status_code=500, detail="No se pudo asignar token")

@app.post("/autorizar-acceso")
def autorizar(data: dict, rol: str = Depends(get_rol)):
    if rol != data.get("rol_usuario"):
        raise HTTPException(status_code=403, detail="Acceso denegado por rol")
    return {"mensaje": "Acceso autorizado", "recursos": data.get("recursos")}
