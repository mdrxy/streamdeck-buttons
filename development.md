# Development - Stream Deck Button Tracker

## Docker Compose

Start the local stack with Docker Compose:

```sh
docker compose watch
```

Now you can open your browser and interact with these URLs:

- Frontend, built with Docker, with routes handled based on the path: <http://localhost:5173>
- Backend, JSON based web API based on OpenAPI: <http://localhost:8000>
  - Automatic interactive documentation with Swagger UI (from the OpenAPI backend): <http://localhost:8000/docs>
- Adminer, database web administration: <http://localhost:8080>
- Traefik UI, to see how the routes are being handled by the proxy: <http://localhost:8090>

## Local Development

The Docker Compose files are configured so that each of the services is available in a different port in `localhost`.

For the backend and frontend, they use the same port that would be used by their local development server, so, the backend is at `http://localhost:8000` and the frontend at `http://localhost:5173`.

This way, you could turn off a Docker Compose service and start its local development service, and everything would keep working, because they use the same ports.

For example, you can stop the  `frontend`:

```sh
docker compose stop frontend
```

And then start the local frontend development server:

```sh
cd frontend
npm run dev
```

For `backend`:

```sh
docker compose stop backend
cd backend
fastapi dev app/main.py
```

## Docker Compose in `localhost.tiangolo.com`

When you start the Docker Compose stack, it uses `localhost` by default, with different ports for each service (backend, frontend, adminer, etc).

Deploying to production (or staging), it will deploy each service at a different subdomain, e.g. `api.example.com`.

In the guide about [deployment](DEPLOYMENT.md) you can read about Traefik, the configured proxy. That's the component in charge of transmitting traffic to each service based on the subdomain.

If you want to test that it's all working locally, you can edit the local `.env` file, and change `DOMAIN`, which will be used by Docker Compose to configure the base domain for the services:

```dotenv
DOMAIN=localhost.tiangolo.com
```

Traefik will use this to transmit traffic at `api.localhost.tiangolo.com` to the backend, and traffic at `dashboard.localhost.tiangolo.com` to the frontend.

The domain `localhost.tiangolo.com` is a special domain that is configured (with all its subdomains) to point to `127.0.0.1`. This way you can use that for your local development.

After you update it, run again:

```sh
docker compose watch
```

When deploying to production, the main Traefik is configured outside of the Docker Compose files. For local development, there's an included Traefik in `docker-compose.override.yml`, just to let you test that the domains work as expected, for example with `api.localhost.tiangolo.com` and `dashboard.localhost.tiangolo.com`.

## Docker Compose files and env vars

There is a main `docker-compose.yml` file with all the configurations that apply to the whole stack, it is used automatically by `docker compose`.

There's also a `docker-compose.override.yml` with overrides for development, for example to mount the source code as a volume. It is used automatically by `docker compose` to apply overrides on top of `docker-compose.yml`.

These Docker Compose files use the `.env` file containing configurations to be injected as environment variables in the containers.

They also use some additional configurations taken from environment variables set in the scripts before calling the `docker compose` command.

After changing variables, make sure you restart the stack:

```sh
docker compose watch
```

## Pre-commits and code linting

We use [pre-commit](https://pre-commit.com/) for code linting and formatting.

It runs right before making a commit in git; this ensures that the code is consistent and formatted before committed.

`.pre-commit-config.yaml` contains the config at the root of this project.

### Install pre-commit to run automatically

`pre-commit` is already part of the dependencies of the project, but you could also install it globally if you prefer to, following [the official pre-commit docs](https://pre-commit.com/) or using [Homebrew](https://formulae.brew.sh/formula/pre-commit#default).

After having the `pre-commit` tool installed and available, you need to "install" it in the local repository, so that it runs automatically before each commit:

```sh
pre-commit install
```

It should come return `pre-commit installed at .git/hooks/pre-commit`.

Now whenever you try to commit, e.g. with:

```sh
git commit
```

...pre-commit will run and check and format the code you are about to commit, and will ask you to add that code (stage it) with git again before committing.

#### Running pre-commit hooks manually

you can also run `pre-commit` manually on all the files:

```sh
pre-commit run --all-files
```

## URLs

The production or staging URLs would use these same paths, but with your own domain.

### Development URLs

- Frontend: <http://localhost:5173>
- Backend: <http://localhost:8000>
- Automatic Interactive Docs (Swagger UI): <http://localhost:8000/docs>
- Automatic Alternative Docs (ReDoc): <http://localhost:8000/redoc>
- Adminer: <http://localhost:8080>
- Traefik UI: <http://localhost:8090>
- MailCatcher: <http://localhost:1080>

### Development URLs with `localhost.tiangolo.com` Configured

- Frontend: <http://dashboard.localhost.tiangolo.com>
- Backend: <http://api.localhost.tiangolo.com>
- Automatic Interactive Docs (Swagger UI): <http://api.localhost.tiangolo.com/docs>
- Automatic Alternative Docs (ReDoc): <http://api.localhost.tiangolo.com/redoc>
- Adminer: <http://localhost.tiangolo.com:8080>
- Traefik UI: <http://localhost.tiangolo.com:8090>
- MailCatcher: <http://localhost.tiangolo.com:1080>
