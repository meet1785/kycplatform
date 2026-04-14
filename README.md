# 🛡️ Real-Time KYC & Communication Platform

A production-ready full-stack web application for Know Your Customer (KYC) verification with real-time updates and multi-channel notifications.

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Next.js       │────▶│   Django + DRF   │────▶│   PostgreSQL    │
│   (Vercel)      │     │   (DigitalOcean) │     │   (Database)    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                │
                         ┌──────┴──────┐           ┌─────────────────┐
                         │   Redis     │           │  DO Spaces      │
                         │ (Channels + │           │  (File Storage) │
                         │  Celery)    │           └─────────────────┘
                         └─────────────┘
```

## 🚀 Tech Stack

### Backend
- **Django 4.2** + **Django REST Framework 3.14**
- **Django Channels** + **channels-redis** — WebSockets for real-time updates
- **Celery** + **Redis** — Background task processing
- **PostgreSQL** — Primary database
- **Simple JWT** — JWT authentication
- **drf-spectacular** — OpenAPI documentation

### Frontend
- **Next.js 14** (App Router)
- **TypeScript**
- **Tailwind CSS**
- **React Query (@tanstack/react-query)**
- **React Hook Form** + **Zod** — Form validation
- **Axios** — HTTP client

### Infrastructure
- **Docker** + **Docker Compose**
- **Nginx** — Reverse proxy
- **Gunicorn** + **Uvicorn** — ASGI server
- **DigitalOcean Droplet** — Backend hosting
- **Vercel** — Frontend hosting
- **DigitalOcean Spaces** — File storage (S3-compatible)

### Third-Party Integrations
- **Twilio** — SMS + OTP verification + WhatsApp
- **Brevo (Sendinblue)** — Transactional emails
- **KYC API** — Mock KYC provider (replaceable with real provider)

---

## 📁 Project Structure

```
kycplatform/
├── backend/
│   ├── config/                 # Django project settings
│   │   ├── settings/
│   │   │   ├── base.py         # Shared settings
│   │   │   ├── development.py  # Dev settings
│   │   │   └── production.py   # Production settings
│   │   ├── urls.py             # URL routing
│   │   ├── wsgi.py             # WSGI entry point
│   │   └── asgi.py             # ASGI entry point (WebSockets)
│   ├── apps/
│   │   ├── authentication/     # JWT auth, OTP, user management
│   │   ├── kyc/                # KYC workflow, documents, admin
│   │   ├── notifications/      # SMS, WhatsApp, Email notifications
│   │   └── core/               # Shared utilities, permissions
│   ├── websockets/             # Django Channels consumers
│   ├── celery_app.py           # Celery configuration
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/                # Next.js App Router pages
│   │   │   ├── auth/           # Login, Register, OTP
│   │   │   └── dashboard/      # User dashboard
│   │   ├── components/         # Reusable UI components
│   │   ├── hooks/              # Custom React hooks
│   │   ├── lib/                # API client, utilities
│   │   └── types/              # TypeScript types
│   ├── package.json
│   ├── Dockerfile
│   └── .env.example
├── nginx/
│   └── nginx.conf              # Nginx reverse proxy config
├── docker-compose.yml          # Development setup
└── README.md
```

---

## ⚡ Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (recommended)

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/meet1785/kycplatform.git
cd kycplatform

# Configure backend environment
cp backend/.env.example backend/.env
# Edit backend/.env with your settings

# Configure frontend environment
cp frontend/.env.example frontend/.env.local

# Start all services
docker-compose up -d

# Apply database migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser
```

Access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/v1/
- API Docs: http://localhost:8000/api/docs/
- Django Admin: http://localhost:8000/admin/

### Option 2: Manual Setup

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Configure environment
cp .env.example .env
# Edit .env with your database and API credentials

# Apply migrations
python manage.py migrate --settings=config.settings.development

# Create superuser
python manage.py createsuperuser --settings=config.settings.development

# Run development server (HTTP)
python manage.py runserver --settings=config.settings.development

# Run Daphne for WebSocket support
pip install daphne
daphne -p 8000 config.asgi:application

# In a separate terminal, run Celery worker
celery -A celery_app worker --loglevel=info

# Run Celery beat for scheduled tasks
celery -A celery_app beat --loglevel=info
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local

# Run development server
npm run dev
```

---

## 🔑 Environment Variables

### Backend (`backend/.env`)

```env
# Django
SECRET_KEY=your-super-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_SETTINGS_MODULE=config.settings.development

# Database
DB_NAME=kycplatform
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_ACCESS_LIFETIME_MINUTES=60
JWT_REFRESH_LIFETIME_DAYS=7

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000

# Twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Brevo Email
BREVO_API_KEY=xkeysib-xxxx
DEFAULT_FROM_EMAIL=noreply@kycplatform.com
DEFAULT_FROM_NAME=KYC Platform

# DigitalOcean Spaces
USE_SPACES=False  # Set to True in production
SPACES_ACCESS_KEY=your_key
SPACES_SECRET_KEY=your_secret
SPACES_BUCKET_NAME=kycplatform
SPACES_ENDPOINT_URL=https://nyc3.digitaloceanspaces.com
SPACES_REGION=nyc3

# OTP
OTP_EXPIRY_MINUTES=10
OTP_LENGTH=6
```

### Frontend (`frontend/.env.local`)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

---

## 📚 API Documentation

Interactive API documentation is available at `/api/docs/` (Swagger UI) and `/api/redoc/` (ReDoc).

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register/` | Register new user |
| POST | `/api/v1/auth/login/` | Login (get JWT tokens) |
| POST | `/api/v1/auth/logout/` | Logout (blacklist token) |
| POST | `/api/v1/auth/token/refresh/` | Refresh access token |
| GET/PATCH | `/api/v1/auth/profile/` | Get/update profile |
| POST | `/api/v1/auth/otp/request/` | Request OTP |
| POST | `/api/v1/auth/otp/verify/` | Verify OTP |
| POST | `/api/v1/auth/password/change/` | Change password |

### KYC Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/PUT | `/api/v1/kyc/application/` | Get/update KYC application |
| POST | `/api/v1/kyc/application/submit/` | Submit for verification |
| GET/POST | `/api/v1/kyc/documents/` | List/upload documents |
| GET/DELETE | `/api/v1/kyc/documents/{id}/` | Get signed URL / Delete |

### Admin Endpoints (Staff only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/kyc/admin/applications/` | List all KYC applications |
| POST | `/api/v1/kyc/admin/applications/{id}/review/` | Approve/reject |
| POST | `/api/v1/kyc/admin/applications/{id}/trigger/` | Trigger verification |
| GET | `/api/v1/kyc/admin/applications/{id}/logs/` | View audit logs |

### Notification Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/notifications/` | List notifications |
| PATCH | `/api/v1/notifications/{id}/read/` | Mark as read |
| POST | `/api/v1/notifications/mark-all-read/` | Mark all as read |

### WebSocket

Connect to `ws://host/ws/kyc/` with JWT token in query string:
```
ws://localhost:8000/ws/kyc/?token=<access_token>
```

**Message Types:**
- `connection_established` — Initial connection confirmation
- `kyc_update` — KYC status changed
- `notification` — New notification
- `ping/pong` — Keep-alive

---

## 🚢 Deployment

### Backend on DigitalOcean

1. **Create a Droplet** (Ubuntu 22.04, 2GB+ RAM)

2. **Install dependencies:**
   ```bash
   apt-get update && apt-get install -y docker.io docker-compose nginx certbot
   ```

3. **Clone and configure:**
   ```bash
   git clone https://github.com/meet1785/kycplatform.git
   cd kycplatform
   cp backend/.env.example backend/.env
   # Edit backend/.env with production values
   ```

4. **Run with Docker Compose:**
   ```bash
   docker-compose -f docker-compose.yml up -d
   docker-compose exec backend python manage.py migrate
   docker-compose exec backend python manage.py createsuperuser
   ```

5. **Configure Nginx:**
   ```bash
   cp nginx/nginx.conf /etc/nginx/sites-available/kycplatform
   ln -s /etc/nginx/sites-available/kycplatform /etc/nginx/sites-enabled/
   # Update server_name in nginx.conf
   nginx -t && systemctl reload nginx
   ```

6. **SSL Certificate:**
   ```bash
   certbot --nginx -d yourdomain.com
   ```

### Frontend on Vercel

1. Push code to GitHub
2. Connect repository to Vercel
3. Set environment variables:
   ```
   NEXT_PUBLIC_API_URL=https://api.yourdomain.com
   NEXT_PUBLIC_WS_URL=wss://api.yourdomain.com
   ```
4. Deploy

### DigitalOcean Spaces Setup

1. Create a Space in your region
2. Create API key with read/write access
3. Set `USE_SPACES=True` in production `.env`
4. Update CORS in Spaces settings to allow your domain

---

## 🧪 Running Tests

```bash
cd backend

# Install dev dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=apps --cov-report=html

# Run specific test file
pytest apps/authentication/tests.py -v
```

---

## 🔄 Background Tasks

Celery tasks are defined in:
- `apps/kyc/tasks.py` — KYC processing, reminders, cleanup
- `apps/notifications/tasks.py` — Notification delivery

**Periodic Tasks (Celery Beat):**
Configure in Django Admin → Periodic Tasks:
- Daily KYC reminders: `apps.kyc.tasks.send_kyc_reminder`
- Clean expired URLs: `apps.kyc.tasks.cleanup_expired_documents`

---

## 🛡️ Security

- JWT tokens with short expiry (60 min access, 7 day refresh)
- Token blacklisting on logout
- HTTPS-only in production
- Signed URLs for document access (no direct public access)
- CORS configured for specific origins
- No secrets in codebase (use .env)

---

## 📄 License

MIT License