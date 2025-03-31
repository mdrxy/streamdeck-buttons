# Stream Deck Button Tracker

This is a full-stack web app used to track button usage on a [Stream Deck device](https://www.elgato.com/us/en/s/welcome-to-stream-deck).

## How it Works

By using a [multi action](https://help.elgato.com/hc/en-us/articles/360027960912-Elgato-Stream-Deck-Multi-Actions) on the Stream Deck, you can send background `GET` requests any time a button (AKA "key") is used for other purposes, such as playing a sound effect.

With this app, you can create a list of buttons in a database and assign a unique URL to each button. When the button is pressed, the app will log the button press in the database. Optional de-duplication can be performed to avoid multiple logs for the same button press (e.g. in accidental double-clicks).

### Example Use Case

I am the sysadmin and developer at a [small college radio station](https://github.com/WBOR-91-1-FM). We have a [Stream Deck device that we use to play PSAs](https://mdrxy.com/essays/cartwall.html), station IDs, and sound effects. To maintain FCC compliance, we need to log when PSAs are played. While we do keep logs in Spinitron, it relies on human input to track when a PSA is played. This is not always accurate, as it can be difficult to remember to manually log each PSA.

Furthermore, I wanted to track how often each button is used to help us understand which buttons are most popular and which ones we might want to replace or update.

## Technology Stack and Features

This project borrows from the Full Stack FastAPI Template [(template info)](./TEMPLATE-INFO.md). While it has been kept mostly intact, it has been slimmed down to suit the needs of this project. We use:

- ⚡ [**FastAPI**](https://fastapi.tiangolo.com) for the Python backend API.
  - 🧰 [SQLModel](https://sqlmodel.tiangolo.com) for SQL database interactions (ORM).
  - 🔍 [Pydantic](https://docs.pydantic.dev), for data validation and settings management.
  - 💾 [PostgreSQL](https://www.postgresql.org) as the database.
  - ✅ Tests with [Pytest](https://pytest.org).
- 🚀 [React](https://react.dev) for the frontend.
  - 💃 Using TypeScript, hooks, Vite, and other parts of a modern frontend stack.
  - 🎨 [Chakra UI](https://chakra-ui.com) for the frontend components.
  - 🤖 An automatically generated frontend client.
  - 🧪 [Playwright](https://playwright.dev) for End-to-End testing.
  - 🦇 Dark mode support!
- 🐋 [Docker Compose](https://www.docker.com) for development and production.
- 🔒 Secure password hashing by default.
- 🔑 JWT (JSON Web Token) authentication.
- 📫 Email based password recovery.
- 📞 [Traefik](https://traefik.io) as a reverse proxy / load balancer.

## Usage & Development

- Usage instructions: [USAGE.MD](./USAGE.MD).
- General development docs: [DEVELOPMENT.md](./DEVELOPMENT.md).
- Backend docs: [backend/README.md](./backend/README.md).
- Frontend docs: [frontend/README.md](./frontend/README.md).
- Deployment docs: [DEPLOYMENT.md](./DEPLOYMENT.md).

## License

This project is built on the Full Stack FastAPI Template [(template info)](./TEMPLATE-INFO.md). This template is licensed under the terms of the MIT license. Following suit, this project is also licensed under the terms of the MIT license. See [LICENSE](./LICENSE) for details.
