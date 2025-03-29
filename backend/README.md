# Backend - Stream Deck Button Tracker

## Overview

This is the FastAPI backend service for the Stream Deck Button Tracker project. It handles API requests, authentication, and database interactions. It is designed to work with the frontend and other components of the project.

## Requirements

* [Docker Engine (compose >= 2.20)](https://www.docker.com/).
* [uv](https://docs.astral.sh/uv/) for local Python development (package and environment management).

## Development Setup

### Environment

From `./backend/` you can install all the dependencies with `uv`. You must first create a virtual environment:

```sh
uv venv --python=3.12
uv sync
```

Then you can activate the virtual environment with:

```sh
source .venv/bin/activate
```

Make sure your editor (e.g. VSCode) is using the correct Python virtual environment (3.12), with the interpreter at `backend/.venv/bin/python`.

Modify or add SQLModel models for data and SQL tables in `./backend/app/models.py`, API endpoints in `./backend/app/api/`, CRUD (Create, Read, Update, Delete) utils in `./backend/app/crud.py`.

#### VS Code

There are already configurations in place to run the backend through the VS Code debugger, so that you can use breakpoints, pause and explore variables, etc.

The setup is also already configured so you can run the tests through the VS Code Python tests tab.

### Docker Compose Override

Use the Docker Compose development override to mount the local code and enable live reloading. For example, the directory with the backend code is synchronized in the Docker container, copying the code you change live to the directory inside the container. That allows you to test your changes right away, without having to build the Docker image again. It should only be done during development, for production, you should build the Docker image with a recent version of the backend code. But during development, it allows you to iterate very fast.

To run the backend with the Docker Compose override, you can use:

```sh
docker compose -f docker-compose.yml -f docker-compose.override.yml up
```

The override runs `fastapi run --reload` instead of the default `fastapi run`, which reloads the process whenever the code changes. Keep in mind that if you have a syntax error and save the Python file, it will break and exit, and the container will stop. After that, you can restart the container by fixing the error and running again:

```sh
docker compose watch
```

There is also a commented out `command` override, you can uncomment it and comment the default one. It makes the backend container run a process that does "nothing", but keeps the container alive. That allows you to get inside your running container and execute commands inside, for example a Python interpreter to test installed dependencies, or start the development server that reloads when it detects changes.

To get inside the container with a `bash` session you can start the stack with:

```sh
docker compose watch
```

and then in another terminal, `exec` inside the running container:

```sh
docker compose exec backend bash
```

You should see an output like:

```sh
root@7f2607af31c3:/app#
```

that means that you are in a `bash` session inside your container, as a `root` user, under the `/app` directory, this directory has another directory called "app" inside, that's where your code lives inside the container: `/app/app`.

There you can use the `fastapi run --reload` command to run the debug live reloading server.

```sh
fastapi run --reload app/main.py
```

This runs the live reloading server that auto reloads when it detects code changes.

Nevertheless, if it doesn't detect a change but a syntax error, it will just stop with an error. But as the container is still alive and you are in a Bash session, you can quickly restart it after fixing the error, running the same command.

## Running Tests

Backend tests use [Pytest](https://docs.pytest.org/en/latest/).

To run tests:

```sh
cd backend
bash ./scripts/test.sh
```

During development, modify and add tests in `./backend/app/tests/`.

### Test a Running Stack

If your stack is already up and you just want to run the tests, you can use:

```sh
docker compose exec backend bash scripts/tests-start.sh
```

That `/app/scripts/tests-start.sh` script just calls `pytest` after making sure that the rest of the stack is running. If you need to pass extra arguments to `pytest`, you can pass them to that command and they will be forwarded.

### Test Coverage

When the tests are run, a file [`htmlcov/index.html`](./backend/htmlcov/index.html) is generated, you can open it in your browser to see the coverage of the tests.

## Database Migrations

Make sure you create a "revision" of your models and that you "upgrade" your database with that revision every time you change them. As this is what will update the tables in your database. Otherwise, your application will have errors.

### Creating and Applying Migrations

Important: The backend source code is mounted inside the backend container.

If you run alembic revision inside the container, the migration file will appear in your local filesystem at `backend/app/alembic/versions/`.

If it doesn't show up:

* Make sure you're running inside the running backend container.
* Make sure you're not accidentally in the prestart container (prestart runs migrations at startup but doesn't generate revisions).
* Make sure docker-compose.override.yml is loaded (it mounts the backend source tree).

#### Workflow Example

1. Modify your models.
2. Create and apply the migration:

    Alembic is already configured to import the SQLModel models from `./backend/app/models.py`.

    ```sh
    # Enter backend container
    docker compose exec backend bash

    # Generate migration (local file will be created in backend/app/alembic/versions)
    alembic revision --autogenerate -m "Add column foo to Bar"

    # Apply migration (this is what will actually change the database)
    alembic upgrade head
    ```

3. Verify that the migration file exists locally outside of the container (`exit`):

    ```sh
    ls backend/app/alembic/versions/
    ```

4. Commit the new revision file. It will be in your repo, not trapped inside the container.

**Why does the file appear locally?**

The `docker-compose.override.yml` mounts `./backend` into `/app` in the container.

Any file created in `/app` (inside the container) will appear locally at `./backend`.

If you generate a migration without this volume mount (inside a production container), the file will be inside the container only and lost when it exits.

TL;DR; always create migrations during development using the dev override setup.

### Migration-free Option

If you don't want to use migrations at all, uncomment the lines in the file at `./backend/app/core/db.py` that end in:

```python
SQLModel.metadata.create_all(engine)
```

and comment the line in the file `scripts/prestart.sh` that contains:

```sh
alembic upgrade head
```

If you don't want to start with the default models and want to remove them / modify them, from the beginning, without having any previous revision, you can remove the revision files (`.py` Python files) under `./backend/app/alembic/versions/`. And then create a first migration as described above.

## Email Templates

The email templates are in `./backend/app/email-templates/`. Here, there are two directories: `build` and `src`. The `src` directory contains the source files that are used to build the final email templates. The `build` directory contains the final email templates that are used by the application.

Before continuing, ensure you have the [MJML extension](https://marketplace.visualstudio.com/items?itemName=attilabuti.vscode-mjml) installed in your VS Code.

Once you have the MJML extension installed, you can create a new email template in the `src` directory. After creating the new email template and with the `.mjml` file open in your editor, open the command palette with `Ctrl+Shift+P` and search for `MJML: Export to HTML`. This will convert the `.mjml` file to a `.html` file and now you can save it in the build directory.

## Other Docs

* [Usage](../USAGE.MD) - general usage instructions.
* [Deployment](../DEPLOYMENT.md) - production deployment instructions.
* [Development](../DEVELOPMENT.md) - development instructions.
