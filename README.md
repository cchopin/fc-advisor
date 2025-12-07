# FC-Advisor

A web application for rating Eve Online Fleet Commanders with customizable badges and leaderboards.

## Features

- Rate Fleet Commanders with customizable badges
- Public leaderboard with rankings
- Admin panel for user and badge management
- Secure authentication with hashed passwords
- Automated CI/CD deployment via GitHub Actions

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

This project includes automated testing and deployment via GitHub Actions.

### Workflow

1. On each push to `main`, the CI pipeline runs tests
2. If tests pass, a webhook triggers automatic deployment on the server
3. The server pulls the latest code and rebuilds the Docker container

### Configuration

To enable automated deployment, configure the following secrets in GitHub repository settings:

- `DEPLOY_WEBHOOK_URL`: The deployment webhook endpoint
- `WEBHOOK_SECRET`: Secret token for webhook authentication

## Security

- Passwords are hashed using scrypt
- CSRF protection enabled on all forms
- Session cookies configured with secure flags
- Webhook endpoints protected by secret token authentication

## License

MIT
