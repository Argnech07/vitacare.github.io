import os
from sqlalchemy import create_engine, pool
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

load_dotenv()  # Carga las variables de entorno del .env

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_DB = os.getenv("MYSQL_DB")
    MYSQL_PORT = os.getenv("MYSQL_PORT", 3306)

    if MYSQL_USER and MYSQL_HOST and MYSQL_DB:
        MYSQL_PASSWORD = "" if MYSQL_PASSWORD is None else MYSQL_PASSWORD
        DATABASE_URL = (
            f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
            f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"
        )

if not DATABASE_URL:
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST")
    POSTGRES_DB = os.getenv("POSTGRES_DB")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5432)

    if POSTGRES_USER and POSTGRES_PASSWORD and POSTGRES_HOST and POSTGRES_DB:
        DATABASE_URL = (
            f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
            f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        )

if not DATABASE_URL:
    raise RuntimeError(
        "Database configuration missing. Set DATABASE_URL or provide a complete set of MYSQL_* or POSTGRES_* variables."
    )

# Activar logs SQL solo si se especifica en variables de entorno (útil para debugging)
SQL_ECHO = os.getenv("SQL_ECHO", "false").lower() == "true"

# Configuración de SSL para conexiones remotas MySQL
connect_args = {}
if DATABASE_URL.startswith("mysql"):
    # Configurar SSL
    if os.getenv("MYSQL_SSL", "true").lower() == "true":
        connect_args["ssl"] = {"ssl_mode": "PREFERRED"}
    
    # Configurar timeouts para conexiones remotas inestables
    connect_args["connect_timeout"] = 30
    connect_args["read_timeout"] = 60
    connect_args["write_timeout"] = 60

# Pool configuration for unstable remote connections
pool_config = {
    "pool_size": 5,
    "max_overflow": 10,
    "pool_timeout": 30,
    "pool_recycle": 3600,  # Recycle connections after 1 hour
    "pool_pre_ping": True,  # Test connections before using them
}

engine = create_engine(
    DATABASE_URL,
    echo=SQL_ECHO,
    connect_args=connect_args,
    **pool_config
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
