# VitaCare Backend - Guía de Configuración para VPS

## 1. Configuración del Backend en VPS

### Instalar dependencias
```bash
cd /home/user/VitaCare-Backend-Para-VPS
pip install -r requirements.txt
```

### Iniciar el backend con Uvicorn
```bash
cd /home/user/VitaCare-Backend-Para-VPS
# Opción 1: Directo (para pruebas)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Opción 2: Con Gunicorn (para producción)
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

### Crear servicio systemd (recomendado)
Crear archivo `/etc/systemd/system/vitacare.service`:

```ini
[Unit]
Description=VitaCare FastAPI Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/home/user/VitaCare-Backend-Para-VPS
ExecStart=/usr/local/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Activar:
```bash
sudo systemctl daemon-reload
sudo systemctl enable vitacare
sudo systemctl start vitacare
```

## 2. Configuración Nginx (Proxy Inverso)

Crear `/etc/nginx/sites-available/vitacare`:

```nginx
server {
    listen 80;
    server_name api.vqvsystem.com v.vqvsystem.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Activar:
```bash
sudo ln -s /etc/nginx/sites-available/vitacare /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 3. SSL con Certbot (HTTPS)
```bash
sudo certbot --nginx -d api.vqvsystem.com -d v.vqvsystem.com
```

## 4. Verificación

Probar que el backend responde:
```bash
curl https://v.vqvsystem.com/prescriptions/verify/RC-2026-017
```

## Archivos incluidos en este paquete:
- `vitacare.service` - Servicio systemd
- `nginx-vitacare.conf` - Configuración Nginx
- `.htaccess` - Alternativa para cPanel (si no tienes VPS)
