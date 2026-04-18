# Conquest Portal

A web portal for running a startup accelerator. Startups, mentors, coaches, experts, investors, and admins all log in and do their thing in one place.

- **Startups** manage their profile, book calls with mentors and coaches, respond to forms, track connections.
- **Mentors / Coaches / Experts** publish weekly slot availability, accept meeting requests, view their pod.
- **Alumni and investors** browse startups and request connections.
- **Admins** run the cohort: approve connections, send announcements, schedule events, manage forms.

This is a standalone fork — no dependency on any external Conquest site. Everything runs on your machine, and everything that used to be hardcoded (API URLs, OAuth, Firebase) is now something you configure.

---

## Run it locally

You'll need **Docker**, **Node 18+**, and **Python 3.11+** (only if you poke around the backend outside Docker).

### 1. Start the backend

```bash
cd back/conquest_back
cp .env.example .env        # defaults work for local dev
docker compose up -d --build
```

This brings up Django, Postgres, and Nginx. First build takes 3–5 minutes.

### 2. Load seed data

```bash
docker exec conquest_back_web python manage.py loaddata dump_clean.json
```

You get 232 users (real cohort: 27 startups + mentors + coaches + experts), 52 meeting slots, forms with answers — everything needed to click around.

> If this errors with *contenttypes already exist*, run `docker exec conquest_back_web python manage.py shell -c "import json; data=json.load(open('dump.json')); json.dump([r for r in data if r['model'] not in ('contenttypes.contenttype','auth.permission')], open('dump_clean.json','w'))"` first to generate `dump_clean.json`.

### 3. Create an admin account

```bash
docker exec conquest_back_web python manage.py shell -c "
from django.contrib.auth.models import User
u, _ = User.objects.get_or_create(username='admin', defaults={'is_staff':True, 'is_superuser':True})
u.is_staff = True; u.is_superuser = True
u.set_password('admin123'); u.save()"
```

### 4. Start the frontend

```bash
cd front
cp .env.example .env
# set VITE_API_BASE_URL=http://localhost:9000
npm install
npm run dev
```

Open **http://localhost:5173**.

---

## Log in

After loading seed data, every user's password is whatever `set_password` you ran (during dev, `password123` is the convention if you batch-reset all users — see *Resetting passwords* below).

| Role | Username to try |
|---|---|
| Test startup | `startup1`, `startup2`, `startup3` |
| Real startup | `Prodancy419`, `RTIwala771`, `subtl.ai571`, `Alchemyst386`, `Qlan506` (many more) |
| Mentor | `mentor1`, `mentor2` |
| Coach | `coach1`, `coach2` |
| Expert | `expert1`, `expert2` |
| Admin | `admin` (password `admin123`) |

The Django admin (for admin-level edits) lives at **http://localhost:1399/api/admin/**.

### Resetting passwords

If you just loaded the dump and logins don't work, the dump's password hashes are old. Batch-reset everyone to a known password:

```bash
docker exec conquest_back_web python manage.py shell -c "
from django.contrib.auth.models import User
for u in User.objects.all():
    u.set_password('password123'); u.save()"
```

---

## What works out of the box vs. what needs credentials

| Feature | Needs | Without it |
|---|---|---|
| Username/password login | Nothing | ✅ Works |
| All dashboards, meetings, forms, connections | Nothing | ✅ Works |
| Django admin | Just `createsuperuser` | ✅ Works |
| **Sign in with Google** | Google OAuth Client ID | Button appears, login fails |
| **File uploads (forms, logos)** | Firebase project | Upload fails |
| Outbound email (password resets, invites) | AWS SES account | Email actions silently fail |
| Analytics | GA4 Measurement ID | No analytics, app works fine |

If you don't need a feature, leave the corresponding env var blank and the app won't complain.

---

## Getting credentials (only when you need them)

### Google Sign-In

1. Go to <https://console.cloud.google.com/>, create (or pick) a project.
2. **APIs & Services → OAuth consent screen** — External, fill in app name and your email, add yourself as a test user.
3. **APIs & Services → Credentials → Create OAuth client ID** → Web application.
4. Authorized JavaScript origins: `http://localhost:5173`. Redirect URIs: same.
5. Copy the Client ID into `front/.env` as `VITE_GOOGLE_OAUTH_CLIENT_ID`.
6. Restart `npm run dev`.

### Firebase Storage (for file uploads)

1. Go to <https://console.firebase.google.com/>, create a project.
2. Click the **web (`</>`) icon** to register a web app.
3. Firebase shows a config snippet. Copy each `apiKey`, `authDomain`, `projectId`, `storageBucket`, `messagingSenderId`, `appId` into the matching `VITE_FIREBASE_*` in `front/.env`.
4. In the project sidebar: **Build → Storage → Get started** (test mode is fine for dev).
5. Restart `npm run dev`.

### Outbound email (AWS SES)

1. <https://console.aws.amazon.com/> → **SES** (pick a region — default in `.env` is `ap-south-1`).
2. **Verified identities → Create identity** — verify the email or domain you want to send from. SES will not send from unverified senders.
3. SES starts in *sandbox mode* (only sends to verified recipients). Request production access when ready to send to real users.
4. **IAM → Users → Create user** with programmatic access and policy `AmazonSESFullAccess` (or scoped to `ses:SendEmail`).
5. Copy the access key and secret into `back/conquest_back/.env`:
   ```
   AWS_ACCESS_KEY_ID=...
   AWS_SECRET_ACCESS_KEY=...
   DEFAULT_FROM_EMAIL=whatever-you-verified@your-domain.com
   ```
6. Restart the backend: `docker compose -f back/conquest_back/docker-compose.yaml up -d`.

### Google Analytics (optional)

1. <https://analytics.google.com/> → Admin → Create property → Web data stream.
2. Copy the Measurement ID (`G-XXXXXXXXXX`) into `VITE_GA_MEASUREMENT_ID` in `front/.env`.

---

## URLs at a glance

| | |
|---|---|
| Portal | http://localhost:5173 |
| Django admin (styled) | http://localhost:1399/api/admin/ |
| API (for tools and curl) | http://localhost:9000/api/ |
| Postgres | localhost:5437 |

---

## Troubleshooting

**Nothing loads on 5173 / blank page flashes then disappears**
Open DevTools console. If you see *"GoogleOAuthProvider"*, `main.jsx` is expecting a valid OAuth client ID — we handle this with a placeholder, so a plain refresh usually fixes it.

**Login returns `{"message":"Invalid credentials."}`**
User probably doesn't exist with that exact username, or the dump's password hash is stale. Verify the user: `docker exec conquest_back_web python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.filter(username__icontains='prodancy'))"`. Batch-reset passwords with the snippet above.

**Django admin has no styling**
You hit port 9000 directly. Gunicorn doesn't serve static files. Use <http://localhost:1399/api/admin/> instead — nginx serves static there.

**`postgres_conquest` container keeps exiting**
Image version drift. `back/conquest_back/docker-compose.yaml` pins `postgres:16`; if you're on an older fork, bump it.

**`npm install` fails on something about `website-overlay/vite`**
This project wires in [website-overlay](https://github.com/aryanjain1891/website-overlay) as a dev dependency. If you don't have it locally, either clone+build it and `npm install file:../website-overlay` from `front/`, or remove the plugin from `front/vite.config.js`.

---

## Project structure (only if you're digging in)

```
conquest-portal/
├── front/                React SPA (Vite). All config in src/config.js.
└── back/conquest_back/   Django + DRF. Env-driven settings.
```

Backend apps: `users`, `meetings`, `forms`, `staff`. Frontend routes: `src/routes/Dashboard/*` — one folder per section (Startups, Mentors, Meetings, Forms, etc.).
