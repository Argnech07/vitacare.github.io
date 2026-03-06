# ============================================
# VitaCare Backend - Guía de Despliegue en Render.com
# ============================================

## PASO 1: Preparar el proyecto

### 1.1 Crear cuenta en Render.com
1. Ve a https://render.com
2. Regístrate con GitHub (más fácil)
3. Verifica tu email

### 1.2 Subir a GitHub (si no está)
```bash
cd VitaCare-Backend-Para-VPS
git init
git add .
git commit -m "Initial commit for Render"
git remote add origin https://github.com/TU_USUARIO/vitacare-backend.git
git push -u origin main
```

## PASO 2: Desplegar en Render

### 2.1 Crear Web Service
1. En Render Dashboard, clic **"New +"** → **"Web Service"**
2. Conecta tu repositorio de GitHub
3. Configuración:
   - **Name**: `vitacare-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 2.2 Configurar Variables de Entorno
En el dashboard de tu servicio, agrega:

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `DATABASE_URL` | (Render la genera automáticamente) | URL de PostgreSQL |
| `SECRET_KEY` | `vitacare-secret-key-2024` | Para JWT |
| `ENVIRONMENT` | `production` | Modo producción |

### 2.3 Crear Base de Datos PostgreSQL
1. En Render Dashboard → **"New +"** → **"PostgreSQL"**
2. **Name**: `vitacare-db`
3. Plan: **Free**
4. Render te dará la `DATABASE_URL` automáticamente

### 2.4 Actualizar código para usar DATABASE_URL

Edita `app/db.py` y asegúrate de leer de `os.environ`:

```python
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./vitacare.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## PASO 3: Obtener URL del Backend

Después del despliegue, Render te dará una URL como:
```
https://vitacare-backend.onrender.com
```

### 3.1 Actualizar Angular
Edita `src/environments/environment.ts`:

```typescript
export const environment = {
  production: true,
  apiUrl: 'https://vitacare-backend.onrender.com',
};
```

## PASO 4: Probar

1. Documentación API: `https://vitacare-backend.onrender.com/docs`
2. Verificar receta: `https://vitacore-backend.onrender.com/prescriptions/verify/RC-2026-017`

## Notas Importantes

### ⚠️ Limitaciones del Plan Gratuito:
- El servidor "duerme" después de 15 min de inactividad
- Se despierta en ~30 segundos al recibir una petición
- 512 MB RAM, 0.5 CPU
- Base de datos de 1 GB

### ✅ Ventajas:
- SSL (HTTPS) automático
- CI/CD automático desde GitHub
- Logs en tiempo real
- No necesitas configurar Nginx

## Solución de Problemas

### Error: "Module not found"
Asegúrate que `requirements.txt` incluya:
```
fastapi
uvicorn
sqlalchemy
psycopg2-binary
pydantic
python-jose
passlib
python-multipart
reportlab
qrcode
pillow
```

### Error de CORS
El backend ya tiene CORS configurado en `main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    ...
)
```

### Base de datos no conecta
Verifica que `DATABASE_URL` esté correctamente seteada en Environment Variables.

## Archivos creados para Render:
- `render.yaml` - Blueprint de configuración
- `Dockerfile` - Alternativa con Docker

## Soporte
Si tienes problemas, revisa los logs en:
Render Dashboard → Tu Servicio → Logs
