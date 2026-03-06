@echo off
chcp 65001 >nul
echo ============================================
echo      VitaCare Backend - Iniciar Servidor
echo ============================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no encontrado. Instala Python 3.9+
    pause
    exit /b 1
)

REM Instalar dependencias si no existen
echo [1/3] Verificando dependencias...
if not exist .venv (
    echo Creando entorno virtual...
    python -m venv .venv
)

REM Activar entorno virtual
call .venv\Scripts\activate.bat

REM Instalar/actualizar dependencias
pip install -q fastapi uvicorn sqlalchemy pydantic python-jose passlib python-multipart reportlab qrcode pillow

echo.
echo [2/3] Iniciando servidor FastAPI...
echo.
echo URL del backend: http://localhost:8000
echo Documentación: http://localhost:8000/docs
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

REM Iniciar Uvicorn
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
