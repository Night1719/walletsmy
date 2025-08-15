#!/usr/bin/env bash
set -euo pipefail

if [[ $(id -u) -ne 0 ]]; then
	echo "Run as root" >&2
	exit 1
fi

echo "--- BG Surveys installer (Ubuntu 24.04) ---"

read -rp "Domain (e.g. surveys.example.com) or IP: " BG_DOMAIN
read -rp "Public URL (e.g. https://surveys.example.com or http://IP): " BG_PUBLIC_URL
read -rp "Admin username: " BG_ADMIN_USER
read -rp "Admin email: " BG_ADMIN_EMAIL
read -rsp "Admin password: " BG_ADMIN_PASS; echo
read -rp "DB name [bg_surveys]: " BG_DB_NAME; BG_DB_NAME=${BG_DB_NAME:-bg_surveys}
read -rp "DB user [bg_surveys]: " BG_DB_USER; BG_DB_USER=${BG_DB_USER:-bg_surveys}
read -rsp "DB password: " BG_DB_PASS; echo
read -rp "LDAP server URI (or empty to skip): " LDAP_URI
if [[ -n "$LDAP_URI" ]]; then
	read -rp "LDAP bind DN: " LDAP_BIND_DN
	read -rsp "LDAP bind password: " LDAP_BIND_PASS; echo
	read -rp "LDAP base DN: " LDAP_BASE_DN
fi

APP_DIR="/opt/bg-surveys"
PY_ENV="$APP_DIR/venv"
USER_SVC="bg-surveys"
PORT=8085

apt-get update -y
DEBIAN_FRONTEND=noninteractive apt-get install -y python3-venv python3-pip python3-dev build-essential postgresql postgresql-contrib nginx git rsync

install -d -o root -g root "$APP_DIR"
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
rsync -a --delete "$SCRIPT_DIR/" "$APP_DIR/"

python3 -m venv "$PY_ENV"
"$PY_ENV/bin/pip" install --upgrade pip
"$PY_ENV/bin/pip" install -r "$APP_DIR/requirements.txt"

# PostgreSQL setup
systemctl enable --now postgresql
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname = '$BG_DB_NAME'" | grep -q 1 || sudo -u postgres createdb "$BG_DB_NAME"
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname = '$BG_DB_USER'" | grep -q 1 || sudo -u postgres psql -c "CREATE USER \"$BG_DB_USER\" WITH PASSWORD '$BG_DB_PASS';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE \"$BG_DB_NAME\" TO \"$BG_DB_USER\";" || true

# Prepare .env
SECRET=$(python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(32))
PY
)
cat > "$APP_DIR/.env" <<EOF
APP_NAME=BG Surveys
APP_DESCRIPTION=Corporate survey platform for Banter Group
APP_VERSION=0.1.0
SECRET_KEY=$SECRET
DATABASE_URL=postgresql+psycopg2://$BG_DB_USER:$BG_DB_PASS@localhost:5432/$BG_DB_NAME
DOMAIN=$BG_DOMAIN
PUBLIC_URL=$BG_PUBLIC_URL
BOOTSTRAP_ADMIN_USERNAME=$BG_ADMIN_USER
BOOTSTRAP_ADMIN_EMAIL=$BG_ADMIN_EMAIL
BOOTSTRAP_ADMIN_PASSWORD=$BG_ADMIN_PASS
LDAP_SERVER_URI=${LDAP_URI:-}
LDAP_BIND_DN=${LDAP_BIND_DN:-}
LDAP_BIND_PASSWORD=${LDAP_BIND_PASS:-}
LDAP_BASE_DN=${LDAP_BASE_DN:-}
EOF

# Create DB tables and bootstrap admin
"$PY_ENV/bin/python" - <<'PY'
from app.config import settings
from app.database import engine, SessionLocal
from app.models import Base, User
from app.auth import hash_password

Base.metadata.create_all(bind=engine)

from sqlalchemy.orm import Session

db: Session = SessionLocal()
try:
	user = db.query(User).filter(User.username==settings.BOOTSTRAP_ADMIN_USERNAME).first()
	if not user:
		user = User(username=settings.BOOTSTRAP_ADMIN_USERNAME, email=settings.BOOTSTRAP_ADMIN_EMAIL, password_hash=hash_password(settings.BOOTSTRAP_ADMIN_PASSWORD), role='admin', is_active=True)
		db.add(user)
		db.commit()
finally:
	db.close()
PY

# Systemd service
cat > "/etc/systemd/system/$USER_SVC.service" <<EOF
[Unit]
Description=BG Surveys (FastAPI)
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$APP_DIR
EnvironmentFile=$APP_DIR/.env
ExecStart=$PY_ENV/bin/uvicorn app.main:app --host 0.0.0.0 --port $PORT
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now "$USER_SVC"

# Nginx
cat > "/etc/nginx/sites-available/$USER_SVC" <<EOF
server {
	listen 80;
	server_name $BG_DOMAIN;
	client_max_body_size 20m;

	location /static/ {
		alias $APP_DIR/app/static/;
	}

	location / {
		proxy_pass http://127.0.0.1:$PORT;
		proxy_set_header Host $host;
		proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		proxy_set_header X-Forwarded-Proto $scheme;
	}
}
EOF

ln -sf "/etc/nginx/sites-available/$USER_SVC" "/etc/nginx/sites-enabled/$USER_SVC"
nginx -t
systemctl restart nginx

echo "Installation complete. Visit: $BG_PUBLIC_URL"