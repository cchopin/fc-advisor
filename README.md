# FC-Advisor

A web application for rating Eve Online Fleet Commanders with customizable badges and leaderboards.

## Features

- Rate Fleet Commanders with customizable badges
- Public leaderboard with rankings
- Admin panel for user and badge management
- Secure authentication with hashed passwords
- CI via GitHub Actions, pull-based auto-deploy on the server

## Requirements

- Docker and Docker Compose
- Git

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/cchopin/fc-advisor.git
cd fc-advisor
```

### 2. Create the data directory

```bash
mkdir -p data
```

### 3. Start the application

```bash
docker compose up -d
```

### 4. Create an admin user

```bash
docker compose exec web python -m app.create_admin <username> <password>
```

### 5. Access the application

- Application: `http://localhost:5050`
- Admin panel: `http://localhost:5050/auth/login`

## Usage

### Docker commands

| Command | Description |
|---------|-------------|
| `docker compose up -d` | Start the application |
| `docker compose down` | Stop the application |
| `docker compose logs -f` | View application logs |
| `docker compose restart` | Restart the application |

## CI/CD

### Workflow

1. On each push to `main`, GitHub Actions runs the tests
2. Every 2 minutes, a systemd timer on the server checks `main` on GitHub
3. When `main` has a new commit whose CI checks all passed, the server
   fast-forwards, rebuilds the container and checks that the app responds

The server only makes outbound requests, so no inbound port or webhook is needed.

### Server setup

```bash
cp .env.example .env   # then set SECRET_KEY
sudo cp deploy/fc-advisor-autodeploy.{service,timer} /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now fc-advisor-autodeploy.timer
journalctl -u fc-advisor-autodeploy -f   # deployment logs
```

The deploy is skipped while the working tree has uncommitted changes.

## Security

- Passwords are hashed using scrypt
- CSRF protection enabled on all forms
- Session cookies configured with secure flags

## License

MIT
