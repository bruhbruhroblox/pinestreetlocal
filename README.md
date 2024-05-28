<p align="center">
  <a href="https://wallstreetlocal.com" target="_blank">
    <picture>
      <img alt="wallstreetlocal" src="https://raw.githubusercontent.com/leftmove/pinestreetlocal/main/static/logo.png" style="max-width: 100%;">
    </picture>
  </a>
</p>

<p align="center">
  A website that allows you to view the investments of America's largest investors.
</p>
<p align="center">
  This repository holds the back-end code for wallstreetlocal, for the front-end, see <a href="https://github.com/leftmove/walltreetlocal" target="_blank" >here</a>.
</p>

<h2 align="center">
  This repository is deprecated. The code was merged into wallstreetlocal's <a src="https://github.com/leftmove/wallstreetlocal">main repository</a>.
</h2>

### Getting Started

This project uses Docker, to deploy, run the following command.

```bash
docker compose up -f docker-compose.yaml up
```

#### Third Party APIs

To run both the development and production builds, you will need to have environment variables for third party APIs. Most of the environment variables in the provided compose files you can keep as is, but for the API keys you will need to visit the following services.

- [Alpha Vantage](https://www.alphavantage.co/)
- [OpenFIGI](https://www.openfigi.com/)
- [Finnhub](https://finnhub.io/)

These three different services allow for the most up-to-date and accurate data, while also avoiding rate-limiting.

#### Telemetry

For telemetry, wallstreetlocal uses [Sentry](https://sentry.io/). You can sign up [here](https://sentry.io/signup/).

_Sentry is a paid service, although it has a free trial. If you are a student, there is also a free upgrade available._

### Development

The development build is mainly made for testing, so it is ideal for self-hosting.

A full list of this app's microservices.

- FastAPI for the main application
- MongoDB for the database
- Redis for cache
- Meilisearch for search
- Sentry for telemetry

To run the full app, you need the microservices running through Docker, and the main application running seperately.

1. Run the microservices by calling the development `docker-compose.yaml`.

```bash
docker compose -f docker-compose.yaml up
```

2. Run the main application (with configured environment variables).

```bash
python main.py
```

`docker-compose.yaml` (Development)

```yaml
services:
  cache:
    container_name: cache
    build:
      context: ./cache
      dockerfile: Dockerfile
    restart: always
    networks:
      - staging
    ports:
      - 6379:6379
  database:
    container_name: database
    build:
      context: ./database
      dockerfile: Dockerfile
    volumes:
      - ./database/main_db:/data/db
    restart: always
    networks:
      - staging
    ports:
      - 27017:27017
  search:
    container_name: search
    build:
      context: ./search
      dockerfile: Dockerfile
    volumes:
      - ./search/search_db:/meili_data
    restart: always
    networks:
      - staging
    ports:
      - 7700:7700

networks:
  staging:
    driver: bridge
```

Example `.env` (Development)

```env
SERVER = "127.0.0.1"
APP_NAME = "backend"
ENVIRONMENT = "development"
ADMIN_PASSWORD = "***********"
DEBUG_CIK = "1067983"

WORKERS = 1
HOST = "0.0.0.0"
EXPOSE_PORT = 8000
FORWARDED_ALLOW_IPS = "*"

FINN_HUB_API_KEY ="***********"
ALPHA_VANTAGE_API_KEY ="***********"
OPEN_FIGI_API_KEY = "***********"

MONGO_SERVER_URL = "mongodb://${SERVER}:27017"
MONGO_BACKUP_URL = "1LT4xiFJkh6YlAPQDcov8YIKqcvevFlEE"

REDIS_SERVER_URL = "${SERVER}"
REDIS_PORT = 6379

MEILI_SERVER_URL = "http://${SERVER}:7700"
MEILI_MASTER_KEY = "***********"

SENTRY_DSN = ""
TELEMETRY = False
```

### Production

The production build is made for running at scale, so you may want to do the following things:

- Run on only one worker
- Map all docker ports to `localhost`

To run the full application with all required microservices, you need just one command.

```bash
docker compose -f docker-compose.yaml up
```

`docker-compose.yaml` (Production)

```yaml
version: "3.4"

services:
  backend:
    container_name: backend
    build:
      dockerfile: Dockerfile.prod
    restart: always
    depends_on:
      - database
      - cache
      - search
    volumes:
      - ./public:/app/public
    networks:
      - proxy-network
    environment:
      APP_NAME: "backend"
      ENVIRONMENT: "production"
      ADMIN_PASSWORD: "***********"

      WORKERS: 9
      HOST: "0.0.0.0"
      EXPOSE_PORT: 8000
      FORWARDED_ALLOW_IPS: "*"

      FINN_HUB_API_KEY: "***********"
      ALPHA_VANTAGE_API_KEY: "***********"
      OPEN_FIGI_API_KEY: "***********"

      MONGO_SERVER_URL: "database"
      MONGO_BACKUP_URL: "1LT4xiFJkh6YlAPQDcov8YIKqcvevFlEE"
      REDIS_SERVER_URL: "cache"
      REDIS_PORT: 6379
      MEILI_SERVER_URL: "search"
      MEILI_MASTER_KEY: "***********"

      TELEMETRY: False

  cache:
    container_name: cache
    build:
      context: ./cache
      dockerfile: Dockerfile
    networks:
      - proxy-network
    restart: always

  database:
    container_name: database
    build:
      context: ./database
      dockerfile: Dockerfile
    networks:
      - proxy-network
    volumes:
      - ./database/main_db:/data/db
    restart: always

  search:
    container_name: search
    build:
      context: ./search
      dockerfile: Dockerfile
    volumes:
      - ./search/search_db:/meili_data
    networks:
      - proxy-network
    restart: always

networks:
  proxy-network:
    name: proxy-network
```

#### _If these configuration files do not work for you, they are likely outdated. To fix them, please write an issue._

## License

[MIT License](./LICENSE)

[Community Code of Conduct](./CODE_OF_CONDUCT.MD)
