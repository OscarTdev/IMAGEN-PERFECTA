from fastapi import Request, HTTPException
from app.core.config import LLAVE_SECRETA

# Hash maestro que le darás al profesor
# Puedes cambiarlo por cualquier palabra secreta
HASH_MAESTRO = "c4110dcc43d38829853e4bc00825d54e8bb484a7a4123c753575cd67e2b90760"

async def verificar_permisos_profe(request: Request):
    """
    Middleware simple para validar que el profesor tenga permiso de acceso.
    Busca el hash en la cabecera 'X-Auth-Hash'.
    """
    auth_hash = request.headers.get("X-Auth-Hash")
    if not auth_hash or auth_hash != HASH_MAESTRO:
        raise HTTPException(
            status_code=403,
            detail="Permisos insuficientes: Hash de autorización inválido o ausente."
        )
    return True
