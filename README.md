# URL Shortener API

Acortador de URLs con caché Redis, contador de clicks y expiración automática.

## Stack

- **FastAPI** — Framework web con documentación automática
- **PostgreSQL** — Persistencia de URLs y estadísticas
- **Redis** — Caché con TTL deslizante para redirecciones rápidas
- **Docker + Docker Compose** — Containerización completa
- **pytest** — Suite de tests automatizados
- **GitHub Actions** — CI/CD con tests antes de cada deploy

## Arquitectura

```
Cliente visita URL corta
        ↓
¿Está en Redis? (RAM)
   ↓ sí                    ↓ no (cache miss)
Redirige al instante       Consulta PostgreSQL
Resetea TTL                Guarda en Redis
                           Redirige
```

PostgreSQL es la fuente de verdad. Redis es la capa de velocidad. Si Redis se cae, el sistema sigue funcionando desde PostgreSQL.

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/urls` | Crear URL corta |
| `GET` | `/{code}` | Redirigir a la URL original |
| `GET` | `/urls/{code}/stats` | Ver estadísticas de clicks |
| `GET` | `/health` | Estado del servicio |

## Probarlo ahora

**Crear una URL corta:**
```bash
curl -X POST https://TU_DOMINIO/urls \
  -H "Content-Type: application/json" \
  -d '{"original_url": "https://github.com/JJrendon29", "expires_in_hours": 24}'
```

**Respuesta:**
```json
{
  "code": "abc123",
  "original_url": "https://github.com/JJrendon29",
  "short_url": "https://TU_DOMINIO/abc123",
  "clicks": 0,
  "created_at": "2026-08-03T17:45:56",
  "expires_at": "2026-08-04T17:45:56"
}
```

**Ver estadísticas:**
```bash
curl https://TU_DOMINIO/urls/abc123/stats
```

**Explorar la documentación interactiva:**
```
https://TU_DOMINIO/docs
```

## Decisiones de diseño

**Sliding window TTL** — cada visita a una URL resetea su TTL en Redis. Las URLs populares nunca expiran del caché porque siempre hay alguien visitándolas. Las que nadie usa desaparecen solas.

**410 vs 404** — una URL expirada devuelve `410 Gone` en vez de `404 Not Found`. El 404 significa "nunca existió". El 410 significa "existió pero ya no está disponible". Es semánticamente correcto.

**Expiración obligatoria** — todas las URLs expiran entre 1 hora y 7 días. Default: 1 hora. Mantiene la base de datos limpia sin acumular datos indefinidamente.

## Correr localmente

**Requisitos:** Docker y Docker Compose instalados.

```bash
# 1. Clonar el repositorio
git clone git@github.com:JJrendon29/url-shortener-api.git
cd url-shortener-api

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores

# 3. Levantar los servicios
docker compose up -d --build

# 4. Verificar que funciona
curl http://localhost:8002/health
```

## Tests

```bash
docker compose exec api pytest tests/ -v
```

## Estructura

```
url-shortener-api/
├── app/
│   ├── models/      # Modelo de base de datos
│   ├── schemas/     # Schemas de validación
│   ├── routers/     # Endpoints
│   ├── config.py    # Configuración centralizada
│   ├── database.py  # Conexión a PostgreSQL
│   └── main.py      # Punto de entrada
├── tests/           # Suite de tests con pytest
├── .github/
│   └── workflows/   # Pipeline CI/CD
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## CI/CD

Cada push a `main` ejecuta automáticamente:

1. Tests con pytest — si alguno falla, el deploy no procede
2. Deploy con Docker Compose

Pipeline configurado con GitHub Actions y self-hosted runner.
