from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bcrypt tiene una limitación de 72 bytes para las contraseñas
BCRYPT_MAX_PASSWORD_LENGTH = 72


def _truncate_password_to_bytes(password: str) -> bytes:
    """Trunca la contraseña a 72 bytes como requiere bcrypt"""
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > BCRYPT_MAX_PASSWORD_LENGTH:
        # Truncar a 72 bytes, pero asegurarse de no cortar en medio de un carácter UTF-8
        truncated = password_bytes[:BCRYPT_MAX_PASSWORD_LENGTH]
        # Intentar decodificar y recodificar para evitar caracteres inválidos
        try:
            # Si se cortó en medio de un carácter, eliminar los bytes finales inválidos
            while truncated:
                try:
                    truncated.decode('utf-8')
                    break
                except UnicodeDecodeError:
                    truncated = truncated[:-1]
        except:
            pass
        return truncated
    return password_bytes


def get_password_hash(password: str) -> str:
    """Genera un hash de la contraseña usando bcrypt"""
    # Truncar a máximo 72 bytes ANTES de hashear
    # Bcrypt tiene límite de 72 bytes internamente
    password_truncated = password[:72]  # Cortar a 72 caracteres max
    return pwd_context.hash(password_truncated)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña contra su hash"""
    try:
        # Truncar si es necesario antes de verificar
        password_bytes = _truncate_password_to_bytes(plain_password)
        password_str = password_bytes.decode('utf-8', errors='replace')
        return pwd_context.verify(password_str, hashed_password)
    except (ValueError, TypeError, Exception):
        # Si hay un error con el hash o la contraseña, retornar False
        return False
