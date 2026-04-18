# Conquest Portal

A full-stack startup ecosystem portal: startups, mentors, investors, experts, meetings, forms, and connections. React SPA + Django REST API.

This is an **independent** fork. It does not depend on any conquest.org.in domain. Every external URL and third-party credential is configurable via environment variables so you can run it against your own infrastructure.

---

## Stack

**Frontend** — Vite + React 18, Ant Design, React Router v6, Framer Motion, GSAP, Firebase Storage, Google OAuth, GA4.

**Backend** — Django 5 + Django REST Framework, SimpleJWT auth, PostgreSQL, AWS SES for email, Sentry (optional).

**Infra (dev)** — Docker Compose brings up Django + Postgres + Nginx.

---

## Repo layout

```
conquest-portal/
├── front/                  Vite + React SPA
│   ├── src/config.js       single source of truth for env-driven config
│   └── .env.example        frontend env vars
└── back/conquest_back/     Django project
    ├── conquest_back/      settings.py, urls.py
    ├── users/ meetings/ forms/ staff/
    ├── docker-compose.yaml
    └── .env.example        backend env vars
```

---

## Quick start — frontend only (no backend)

Good for UI work. Login and API-backed pages will not be functional.

```bash
cd front
cp .env.example .env       # leave values blank for now
npm install
npm run dev                # → http://localhost:5173
```

---

## Full local setup

### 1. Backend

```bash
cd back/conquest_back
cp .env.example .env
# edit .env — at minimum set DJANGO_SECRET_KEY, POSTGRES_PASSWORD
docker compose up --build
# API at http://localhost:9000  (via nginx: http://localhost:1399)
```

First run: open a new terminal and apply migrations + create a superuser:

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

### 2. Frontend

```bash
cd front
cp .env.example .env
# set VITE_API_BASE_URL=http://localhost:9000
npm install
npm run dev
```

---

## Environment variables

### Frontend (`front/.env`)

| Variable | What it is |
|---|---|
| `VITE_API_BASE_URL` | Backend origin. `http://localhost:9000` for local dev. |
| `VITE_MARKETING_SITE_URL` | Your marketing/brochure site (alumni/about/privacy pages linked from nav and footer). Leave blank to make those links no-ops. |
| `VITE_CONTACT_EMAIL` | Public contact email shown in footer. |
| `VITE_GA_MEASUREMENT_ID` | Google Analytics 4 ID (`G-XXXX...`). Leave blank to disable. |
| `VITE_GOOGLE_OAUTH_CLIENT_ID` | OAuth 2.0 Web Client ID for "Sign in with Google". |
| `VITE_FIREBASE_*` | Firebase web app config — used for user file uploads to Firebase Storage. |

### Backend (`back/conquest_back/.env`)

| Variable | What it is |
|---|---|
| `DJANGO_SECRET_KEY` | Long random string. `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DJANGO_DEBUG` | `True` for dev, `False` for prod. |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hostnames the backend will answer on. |
| `DJANGO_CORS_ALLOWED_ORIGINS` | Comma-separated full frontend URLs (include scheme). |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Same format. Usually same list as CORS. |
| `POSTGRES_*` | DB name/user/password/host/port. |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_REGION_NAME` | Credentials for SES (outbound email). |
| `DEFAULT_FROM_EMAIL` | Verified sender address in SES. |
| `SENTRY_DSN` | Optional. Leave blank to disable Sentry. |

---

## How to get each credential

### Google OAuth Client ID (for "Sign in with Google")

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (or pick an existing one).
3. Enable the "Google Identity" / People API.
4. Navigate to **APIs & Services → Credentials → Create Credentials → OAuth client ID**.
5. Configure the consent screen first if prompted (External, add your email as a test user).
6. Application type: **Web application**.
7. Authorized JavaScript origins: add `http://localhost:5173` (and your production URL).
8. Authorized redirect URIs: add `http://localhost:5173` (and prod).
9. Copy the **Client ID** → `VITE_GOOGLE_OAUTH_CLIENT_ID`.

### Firebase web app (for file uploads)

1. Go to [Firebase Console](https://console.firebase.google.com/).
2. **Add project** → follow wizard.
3. In the project, click the **web icon (`</>`) to add a web app**.
4. Firebase gives you a config object with `apiKey`, `authDomain`, etc. Copy each value into the matching `VITE_FIREBASE_*` env var.
5. In the left nav: **Build → Storage → Get started**. Pick a region, start in test mode for dev (tighten rules before prod).

### Google Analytics 4 Measurement ID

1. Go to [Google Analytics](https://analytics.google.com/).
2. Admin → Create property → fill in details → finish.
3. Add a **Data Stream** (Web) for your portal URL.
4. Copy the **Measurement ID** (`G-XXXXXXXXXX`) → `VITE_GA_MEASUREMENT_ID`.

### AWS SES (for outbound email)

1. [AWS Console](https://console.aws.amazon.com/) → **SES**.
2. Pick a region (matches `AWS_REGION_NAME`, default `ap-south-1`).
3. **Verified identities → Create identity**: verify your sender email or domain. Without this, SES refuses to send.
4. New accounts start in **sandbox mode** — can only send to verified recipients. Request production access from the SES console when ready.
5. **IAM → Users → Create user** with programmatic access and the policy `AmazonSESFullAccess` (or a scoped `ses:SendEmail` policy).
6. Grab the access key and secret → `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`.
7. Set `DEFAULT_FROM_EMAIL` to your verified sender.

### Sentry DSN (optional)

1. [Sentry.io](https://sentry.io/) → create project (platform: Django).
2. Copy the DSN shown during setup → `SENTRY_DSN`.
3. Leave blank to disable.

---

## Useful commands

```bash
# Backend
docker compose up --build              # start everything
docker compose down                    # stop
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py shell

# Frontend
npm run dev                            # dev server
npm run build                          # production build → dist/
npm run preview                        # preview the production build
npm run lint
```

---

## Notes

- `back/conquest_back/dump.json` is a legacy data fixture from the original deployment. Safe to delete if you don't need it.
- `back/conquest_back/serverNginx*.txt` are deployment notes, not live config. The active nginx config is `back/conquest_back/nginx/default.conf`.
- The in-app "Sign in with Google" button requires **both** `VITE_GOOGLE_OAUTH_CLIENT_ID` on the frontend and the backend endpoint `/api/users/login/google/` to be able to verify tokens (the backend uses `google-auth` libs, which work out of the box as long as the client ID matches what the frontend sends).

---

## License

TBD — add a license file before making this public-facing.
