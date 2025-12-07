# FC-Advisor

A fun application to rate Eve Online Fleet Commanders with humorous badges!

## Quick Start (Docker)

### 1. Prerequisites
- Docker and Docker Compose installed

### 2. Create data folder
```bash
mkdir -p data
```

### 3. Start the app
```bash
docker compose up -d
```

### 4. Create your admin user
```bash
docker compose exec web python -m app.create_admin tely YourSecurePassword
```
(Replace `tely` and `YourSecurePassword` with your desired credentials)

### 5. Access
- App: http://your-server:5050
- Admin: http://your-server:5050/auth/login

## Features
- 🎖️ Rate FCs with fun badges
- 🏆 Leaderboard
- 👥 Admin user management
- 🏷️ Customizable badges

## Commands
```bash
docker compose up -d      # Start
docker compose down       # Stop
docker compose logs -f    # View logs
```

## Security
- Passwords are hashed in database (scrypt)
- No passwords in config files
- CSRF protection enabled
