# ModSecurity WAF Docker Setup

Este repositorio contiene la configuración necesaria para desplegar un Web Application Firewall (WAF) con ModSecurity y Apache, orquestado con Docker Compose.

## Requisitos previos

- Docker
- Docker Compose
- Git

## Instalación

1. Clonar el repositorio:

   ```bash
   git clone https://github.com/enochgitgamefied/Modsecurity-Dashboard.git
   cd Modsecurity-Dashboard
   ```

2. (Opcional) Backend de simulación:

   - Crear un directorio `backend/` en la raíz del repositorio.
   - Dentro de `backend/`, colocar:
     - `app.py`: una pequeña aplicación Flask.
     - `Dockerfile`: define la imagen Python 3.11 + Flask. Esto permite verificar que el WAF filtra correctamente antes de pasar tráfico al backend.

3. Revisar la configuración de Apache + ModSecurity:

   - Archivo: `apache-modsec/apache-config/myapp.conf`
   - Asegurarse de que:
     - El `<VirtualHost>` escuche en el puerto **8880**.
     - `ProxyPass` y `ProxyPassReverse` apunten a `http://backend:8088`.
     - `SecRuleEngine On` esté habilitado.

4. Verificar `docker-compose.yml`:

   - Servicio **waf-dashboard**:
     - Expone puerto **8880** (tráfico HTTP/S).
     - Expone puerto **8000** (dashboard de administración).
   - Servicio **backend**:
     - Expone puerto **8088** internamente.
   - Utiliza una red compartida `waf-net` y volúmenes para logs y reglas personalizadas.

## Levantar el entorno

```bash
docker compose up --build
```

Esperar hasta que ambos contenedores estén en estado "healthy".

## Acceso

- **WAF (proxy inverso + reglas ModSecurity)**:
  ```
  http://localhost:8880
  ```
- **Dashboard de administración**:
  ```
  http://localhost:8000
  ```

---

> **Nota**: Para publicar más aplicaciones detrás del WAF:
>
> 1. Modificar `/etc/apache2/ports.conf` para añadir nuevos `Listen` (por ejemplo `8888`, `8889`).
> 2. Crear un archivo de configuración `.conf` por cada sitio en `/etc/apache2/sites-available/` con su correspondiente `ProxyPass` → backend.
> 3. Ejecutar:
>    ```bash
>    a2ensite <nombre>.conf
>    docker compose restart waf-dashboard
>    ```

