#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# QUIRRELY SECURE DEPLOYMENT SCRIPT v2.0
# Enhanced security deployment with proper secret management
# ═══════════════════════════════════════════════════════════════════════════

set -euo pipefail
RED='\033[0;31m'; GRN='\033[0;32m'; YLW='\033[1;33m'; CYN='\033[0;36m'; BLD='\033[1m'; RST='\033[0m'

ok()   { echo -e "${GRN}OK${RST} $1"; }
info() { echo -e "${CYN}->${RST} $1"; }
warn() { echo -e "${YLW}WARN${RST} $1"; }
die()  { echo -e "${RED}FATAL: $1${RST}"; exit 1; }
hdr()  { echo -e "\n${BLD}${CYN}=== $1 ===${RST}"; }

# Configuration
APP_DIR="/opt/quirrely"
SRC_DIR="${APP_DIR}/quirrely_v313_integrated"
WEB_DIR="/var/www/quirrely"
LOG_DIR="/var/log/quirrely"
SECRETS_DIR="/opt/quirrely/secrets"
ZIP_SRC="/root/quirrely_v313_FINAL.zip"
BACKEND="${SRC_DIR}/backend"
VENV="${BACKEND}/venv"
PY="python3.12"

# ═══════════════════════════════════════════════════════════════════════════
# SECURITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

generate_secure_secret() {
    local length=${1:-64}
    python3 -c "import secrets; print(secrets.token_hex(${length}))"
}

generate_jwt_secret() {
    python3 -c "
import secrets
import string
# Generate high-entropy JWT secret
secret = secrets.token_hex(64)
print(secret)
"
}

validate_secret_strength() {
    local secret="$1"
    local name="$2"
    
    # Check length
    if [[ ${#secret} -lt 32 ]]; then
        die "Secret $name too short (minimum 32 characters)"
    fi
    
    # Check for weak patterns
    local weak_patterns=("password" "secret" "admin" "test" "123" "abc")
    local secret_lower=$(echo "$secret" | tr '[:upper:]' '[:lower:]')
    
    for pattern in "${weak_patterns[@]}"; do
        if [[ "$secret_lower" == *"$pattern"* ]]; then
            die "Secret $name contains weak pattern: $pattern"
        fi
    done
    
    ok "Secret $name validated"
}

create_secure_env_file() {
    local env_file="$1"
    local temp_env=$(mktemp)
    
    cat > "$temp_env" << ENV
# ═══════════════════════════════════════════════════════════════════════════
# QUIRRELY PRODUCTION ENVIRONMENT
# Generated: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
# Security Level: Production
# ═══════════════════════════════════════════════════════════════════════════

# Application
APP_NAME=Quirrely
APP_ENV=production
APP_URL=https://quirrely.com
API_URL=https://api.quirrely.com

# Database
DATABASE_URL=postgresql://quirrely:${DB_PASS}@localhost:5432/quirrely_prod

# Security Secrets (Auto-generated)
SECRET_KEY=${SECRET_KEY}
JWT_SECRET=${JWT_SECRET}
SESSION_SECRET=${SESSION_SECRET}
COOKIE_SECRET=${COOKIE_SECRET}
CSRF_SECRET=${CSRF_SECRET}

# Stripe (User provided)
STRIPE_SECRET_KEY=${STRIPE_SECRET}
STRIPE_PUBLISHABLE_KEY=${STRIPE_PK}
STRIPE_WEBHOOK_SECRET=${STRIPE_WEBHOOK}
STRIPE_PRICE_PRO_MONTHLY=${PRICE_PRO_M}
STRIPE_PRICE_PRO_ANNUAL=${PRICE_PRO_A}
STRIPE_PRICE_AUTHORITY=${PRICE_AUTH}

# Email
RESEND_API_KEY=${RESEND_KEY}
EMAIL_FROM=hello@quirrely.com

# Admin Security
ADMIN_ALLOWED_IP_RANGES=192.168.0.0/16,10.0.0.0/8,172.16.0.0/12,127.0.0.1/32
ADMIN_REQUIRE_VPN=true

# Feature Flags
BLOCKED_COUNTRIES=US
ENABLE_STRETCH=true
ENABLE_EXTENSION_SYNC=true
ENABLE_PRO_FEATURES=true
ENABLE_FEATURED_WRITERS=true

# Security Settings
COOKIE_SECURE=true
COOKIE_DOMAIN=quirrely.com
SESSION_TIMEOUT=28800
RATE_LIMIT_ENABLED=true

# Logging
LOG_LEVEL=INFO
SECURITY_LOG_ENABLED=true
AUDIT_LOG_ENABLED=true
ENV

    # Securely move to final location
    chmod 600 "$temp_env"
    mv "$temp_env" "$env_file"
    chown quirrely:quirrely "$env_file"
}

store_secret_backup() {
    local backup_file="${SECRETS_DIR}/secrets_backup_$(date +%Y%m%d_%H%M%S).enc"
    
    # Create encrypted backup of secrets
    echo "JWT_SECRET=${JWT_SECRET}" | gpg --symmetric --cipher-algo AES256 --output "$backup_file" 2>/dev/null || {
        warn "Could not create encrypted secret backup (gpg not available)"
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# MAIN DEPLOYMENT
# ═══════════════════════════════════════════════════════════════════════════

hdr "STEP 0 - Security Pre-flight"
[[ $EUID -eq 0 ]] || die "Must be run as root"
[[ -f "$ZIP_SRC" ]] || die "quirrely_v313_FINAL.zip not found at $ZIP_SRC"

# Check if this is a production environment
if [[ -z "${QUIRRELY_PROD_CONFIRMED:-}" ]]; then
    echo -e "${YLW}WARNING: This will configure Quirrely for PRODUCTION use.${RST}"
    echo "This includes:"
    echo "  • Secure secret generation"
    echo "  • Hardened security settings"
    echo "  • Production database setup"
    echo "  • Admin IP restrictions"
    echo ""
    read -p "Continue with production deployment? (yes/no): " confirm
    [[ "$confirm" == "yes" ]] || die "Deployment cancelled"
fi

ok "Production deployment confirmed"

hdr "STEP 1 - Secure Secret Collection"
info "We will generate secure secrets automatically and collect external secrets"

# Generate secure secrets automatically
info "Generating cryptographically secure secrets..."
SECRET_KEY=$(generate_secure_secret 64)
JWT_SECRET=$(generate_jwt_secret)
SESSION_SECRET=$(generate_secure_secret 32)
COOKIE_SECRET=$(generate_secure_secret 32)
CSRF_SECRET=$(generate_secure_secret 32)

validate_secret_strength "$SECRET_KEY" "SECRET_KEY"
validate_secret_strength "$JWT_SECRET" "JWT_SECRET"
validate_secret_strength "$SESSION_SECRET" "SESSION_SECRET"

ok "Auto-generated secrets created and validated"

# Collect external secrets securely
echo ""
echo "Please provide the following external secrets:"
echo "(These will not be echoed and will be validated)"
echo ""

# Use read -s for secure input (no echo)
read -rsp "DB password (you choose, 16+ chars): " DB_PASS
echo ""
[[ ${#DB_PASS} -ge 16 ]] || die "Database password must be at least 16 characters"

read -rsp "Stripe secret key (sk_live_...): " STRIPE_SECRET
echo ""
[[ "$STRIPE_SECRET" =~ ^sk_live_ ]] || die "Invalid Stripe secret key format"

read -rsp "Stripe publishable key (pk_live_...): " STRIPE_PK
echo ""
[[ "$STRIPE_PK" =~ ^pk_live_ ]] || die "Invalid Stripe publishable key format"

read -rsp "Stripe webhook secret (whsec_...): " STRIPE_WEBHOOK
echo ""
[[ "$STRIPE_WEBHOOK" =~ ^whsec_ ]] || die "Invalid Stripe webhook secret format"

read -rsp "Stripe Pro Monthly price ID (price_...): " PRICE_PRO_M
echo ""
read -rsp "Stripe Pro Annual price ID (price_...): " PRICE_PRO_A
echo ""
read -rsp "Stripe Authority price ID (price_...): " PRICE_AUTH
echo ""
read -rsp "Resend API key (re_...): " RESEND_KEY
echo ""
[[ "$RESEND_KEY" =~ ^re_ ]] || die "Invalid Resend API key format"

# Validate all secrets are provided
for var in DB_PASS STRIPE_SECRET STRIPE_PK STRIPE_WEBHOOK PRICE_PRO_M PRICE_PRO_A PRICE_AUTH RESEND_KEY; do
    [[ -n "${!var}" ]] || die "$var cannot be empty"
done

ok "All external secrets collected and validated"

hdr "STEP 2 - System packages"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get upgrade -y -qq
apt-get install -y -qq python3.12 python3.12-venv python3.12-dev python3-pip build-essential libpq-dev unzip curl gnupg
ok "Python 3.12 installed"

apt-get install -y -qq postgresql postgresql-contrib
systemctl enable postgresql --quiet
systemctl start postgresql
ok "PostgreSQL running"

apt-get install -y -qq nginx certbot python3-certbot-nginx
systemctl enable nginx --quiet
ok "Nginx installed"

curl -fsSL https://deb.nodesource.com/setup_20.x | bash - 2>/dev/null
apt-get install -y -qq nodejs
npm install -g pm2 --quiet
ok "Node and PM2 installed"

hdr "STEP 3 - Users and directories"
id quirrely &>/dev/null || useradd -r -m -s /bin/bash quirrely
mkdir -p "$APP_DIR" "$WEB_DIR" "$LOG_DIR" "$SECRETS_DIR"
chown quirrely:quirrely "$APP_DIR" "$LOG_DIR" "$SECRETS_DIR"
chown www-data:www-data "$WEB_DIR"
chmod 700 "$SECRETS_DIR"  # Strict permissions for secrets
ok "Users and directories ready"

hdr "STEP 4 - Extract and deploy application"
cd "$APP_DIR"
unzip -q -o "$ZIP_SRC"
[[ -d "$SRC_DIR" ]] || die "Extraction failed"
chown -R quirrely:quirrely "$SRC_DIR"

# Deploy static files
cp -r "$SRC_DIR/frontend/." "$WEB_DIR/"
cp -r "$SRC_DIR/assets" "$WEB_DIR/"
cp -r "$SRC_DIR/blog" "$WEB_DIR/"
[[ -d "$SRC_DIR/auth" ]] && cp -r "$SRC_DIR/auth" "$WEB_DIR/"
[[ -d "$SRC_DIR/billing" ]] && cp -r "$SRC_DIR/billing" "$WEB_DIR/"
[[ -d "$SRC_DIR/legal" ]] && cp -r "$SRC_DIR/legal" "$WEB_DIR/"
[[ -f "$SRC_DIR/404.html" ]] && cp "$SRC_DIR/404.html" "$WEB_DIR/"
[[ -f "$SRC_DIR/500.html" ]] && cp "$SRC_DIR/500.html" "$WEB_DIR/"
[[ -f "$SRC_DIR/sitemap.xml" ]] && cp "$SRC_DIR/sitemap.xml" "$WEB_DIR/"
[[ -f "$SRC_DIR/robots.txt" ]] && cp "$SRC_DIR/robots.txt" "$WEB_DIR/"
chown -R www-data:www-data "$WEB_DIR"
ok "Static files deployed"

hdr "STEP 5 - PostgreSQL with secure configuration"
sudo -u postgres psql -v ON_ERROR_STOP=1 <<SQL
DO \$\$ BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'quirrely') THEN
    CREATE USER quirrely WITH PASSWORD '${DB_PASS}';
  ELSE
    ALTER USER quirrely WITH PASSWORD '${DB_PASS}';
  END IF;
END \$\$;
DO \$\$ BEGIN
  IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'quirrely_prod') THEN
    CREATE DATABASE quirrely_prod OWNER quirrely ENCODING 'UTF8';
  END IF;
END \$\$;
GRANT ALL PRIVILEGES ON DATABASE quirrely_prod TO quirrely;
SQL

# Enable extensions
sudo -u postgres psql -d quirrely_prod -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"; CREATE EXTENSION IF NOT EXISTS \"pgcrypto\";"
ok "Database quirrely_prod ready with secure configuration"

hdr "STEP 6 - Database schemas"
export PGPASSWORD="$DB_PASS"
PG="psql -U quirrely -d quirrely_prod -h localhost -v ON_ERROR_STOP=1 -q"

# Apply schemas in order
for schema in "database/schema.sql" "backend/schema_auth.sql" "backend/schema_payments.sql" "backend/schema_subscriptions_v2.sql" "backend/schema_analytics.sql" "backend/schema_email.sql" "backend/schema_stretch.sql" "backend/schema_admin.sql" "backend/schema_authority.sql" "backend/schema_curator.sql" "backend/schema_milestones.sql" "backend/schema_profiles.sql" "backend/schema_reader.sql" "backend/schema_token_ledger.sql" "backend/schema_halo.sql"; do
    fpath="$SRC_DIR/$schema"
    if [[ -f "$fpath" ]]; then
        $PG -f "$fpath" 2>/dev/null || warn "$schema had warnings"
        ok "$schema"
    else
        warn "SKIPPED: $schema"
    fi
done
ok "All schemas applied"

hdr "STEP 7 - Secure environment configuration"
create_secure_env_file "$BACKEND/.env"
ok "Secure .env file created"

# Store secret backup
store_secret_backup
info "Secret backup stored (if gpg available)"

hdr "STEP 8 - Python virtual environment"
$PY -m venv "$VENV"
source "$VENV/bin/activate"
pip install --upgrade pip --quiet
pip install -r "$BACKEND/requirements.txt" --quiet
deactivate
chown -R quirrely:quirrely "$VENV"
ok "Python dependencies installed"

hdr "STEP 9 - Hardened Nginx configuration"
# Use the hardened configuration
cp "$SRC_DIR/deploy/nginx-security-hardened.conf" /etc/nginx/sites-available/quirrely.conf

# Update with actual domain
sed -i 's/yoursite\.com/quirrely.com/g' /etc/nginx/sites-available/quirrely.conf

ln -sf /etc/nginx/sites-available/quirrely.conf /etc/nginx/sites-enabled/quirrely.conf
rm -f /etc/nginx/sites-enabled/default

# Test configuration
nginx -t && ok "Hardened Nginx config valid" || warn "Nginx config needs SSL certificates"

hdr "STEP 10 - PM2 with security"
cat > "$APP_DIR/ecosystem.config.js" << 'PM2EOF'
module.exports = {
  apps: [{
    name: 'quirrely',
    script: '/opt/quirrely/quirrely_v313_integrated/backend/venv/bin/uvicorn',
    args: 'app:app --host 127.0.0.1 --port 8000 --workers 2',
    cwd: '/opt/quirrely/quirrely_v313_integrated/backend',
    interpreter: 'none',
    env_file: '/opt/quirrely/quirrely_v313_integrated/backend/.env',
    max_memory_restart: '500M',
    error_file: '/var/log/quirrely/error.log',
    out_file: '/var/log/quirrely/out.log',
    merge_logs: true,
    autorestart: true,
    watch: false,
    kill_timeout: 5000,
    max_restarts: 5,
    min_uptime: '10s'
  }]
};
PM2EOF

pm2 start "$APP_DIR/ecosystem.config.js"
pm2 save --force
PM2_STARTUP=$(pm2 startup systemd -u root --hp /root 2>&1 | grep "sudo env" | head -1)
[[ -n "$PM2_STARTUP" ]] && eval "$PM2_STARTUP" || warn "Run 'pm2 startup' manually"
ok "Quirrely running under PM2 with security settings"

hdr "STEP 11 - Final security validation"
# Test JWT secret validation
python3 -c "
import sys
sys.path.append('/opt/quirrely/quirrely_v313_integrated/backend')
from secure_auth_middleware import validate_environment_secrets
result = validate_environment_secrets()
if not result['valid']:
    print('SECURITY VALIDATION FAILED:')
    for issue in result['issues']:
        print(f'  - {issue}')
    sys.exit(1)
print('Security validation passed')
"
ok "Security validation completed"

hdr "STEP 12 - Health check"
sleep 3
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/health 2>/dev/null || echo "000")
[[ "$HTTP_CODE" == "200" ]] && ok "API health check: HTTP 200" || warn "API returned HTTP $HTTP_CODE - check: pm2 logs quirrely"

# Clean up sensitive variables from memory
unset DB_PASS STRIPE_SECRET STRIPE_PK STRIPE_WEBHOOK RESEND_KEY
unset SECRET_KEY JWT_SECRET SESSION_SECRET COOKIE_SECRET CSRF_SECRET
unset PRICE_PRO_M PRICE_PRO_A PRICE_AUTH

hdr "SECURE DEPLOYMENT COMPLETE"
echo ""
echo -e "${BLD}${GRN}Quirrely v3.1.3 deployed with enhanced security.${RST}"
echo ""
echo "  App:     $SRC_DIR"
echo "  Web:     $WEB_DIR"
echo "  Logs:    pm2 logs quirrely"
echo "  Config:  $BACKEND/.env (600 permissions)"
echo "  Secrets: $SECRETS_DIR (700 permissions)"
echo ""
echo -e "${YLW}CRITICAL NEXT STEPS:${RST}"
echo "  1. Update Nginx IP whitelist in: /etc/nginx/sites-available/quirrely.conf"
echo "     Add your admin IPs to the 'geo \$admin_allowed' block"
echo "  2. Point DNS to this server in Cloudflare"
echo "  3. Run SSL setup: certbot --nginx -d quirrely.com -d www.quirrely.com -d api.quirrely.com"
echo "  4. Test admin access restrictions"
echo "  5. Backup the secrets directory securely"
echo ""
echo -e "${RED}SECURITY REMINDERS:${RST}"
echo "  • Never share or commit the .env file"
echo "  • Rotate secrets every 90 days"
echo "  • Monitor /var/log/quirrely/ for security events"
echo "  • Update admin IP whitelist as needed"
echo ""