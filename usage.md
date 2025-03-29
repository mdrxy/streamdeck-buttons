# Usage

## Initial Configuration

Before running or deploying, update your `.env` file with secure values:

- `SECRET_KEY`
- `FIRST_SUPERUSER_PASSWORD`
- `POSTGRES_PASSWORD`

For production, **do not commit the `.env` file**. Pass these values securely via environment secrets.

For deployment details, see [DEPLOYMENT.md](./DEPLOYMENT.md).

### Generating Secret Keys

Anywhere you see `changethis` in `.env`, you need to replace it.

Generate a strong key like this:

```sh
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Development Environment

Start the full stack locally using [Compose Watch](https://docs.docker.com/compose/how-tos/file-watch/):

```sh
docker compose watch
```

This will build and run:

- [Backend API](./backend/README.md) at <http://localhost:8000>
- [Frontend](./frontend/README.md) at <http://localhost:5173>
- [Adminer](#adminer) DB UI at <http://localhost:8080>
- [MailCatcher](#mailcatcher) SMTP UI at <http://localhost:1080>
- [Traefik](#traefik) Dashboard at <http://localhost:8090>

To view logs:

```sh
docker compose logs # All services
docker compose logs backend # For backend logs
```

## Helpers

This app uses a few helper services to make development easier:

### Adminer

Adminer provides a web interface to interact with the database.

To access it, go to <http://localhost:8080>.

- **System**: PostgreSQL
- **Server**: db (the Compose service name)
- **Username**: postgres
- **Password**: `POSTGRES_PASSWORD` from your `.env` file
- **Database**: `POSTGRES_DB` from your `.env` file (default: `app`)

### MailCatcher

MailCatcher is a simple SMTP server that catches emails sent to it and displays them in a web interface. This is useful for testing email functionality without sending real emails over a live SMTP server.

### Traefik

Traefik is a reverse proxy and load balancer that provides a web UI to monitor the services running in your Docker containers. It automatically detects new services and routes traffic to them based on their configuration.
