# 🚀 Bookish — Vercel Deployment Guide

## Prerequisites

1. **Vercel account** — [vercel.com](https://vercel.com)
2. **Hosted PostgreSQL database** — Recommended: **[Neon](https://neon.tech)** (free tier, serverless Postgres, pairs perfectly with Vercel)
3. **Paystack account** — [dashboard.paystack.com](https://dashboard.paystack.com) with API keys
4. **Git repo** — Push this project to GitHub/GitLab/Bitbucket

---

## Step 1: Create a PostgreSQL Database

### Using Neon (recommended)
1. Go to [neon.tech](https://neon.tech) and sign up (free)
2. Create a new project → name it `bookish`
3. Copy the **connection string** — it looks like:
   ```
   postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/bookish?sslmode=require
   ```

> [!TIP]
> You can also use **Supabase**, **Railway**, or **Vercel Postgres** — any hosted PostgreSQL works.

---

## Step 2: Set Up Production Database Tables

Run this **locally** (one-time) with your production database URL:

```powershell
$env:DATABASE_URL = "postgresql://user:password@ep-xxx.neon.tech/bookish?sslmode=require"
$env:FLASK_ENV = "production"
$env:SECRET_KEY = "any-temp-key-for-setup-12345678"
$env:PAYSTACK_SECRET_KEY = "sk_test_your_key_here"

python setup_prod_db.py
```

This creates all tables and seeds the 10 books + categories + demo users.

---

## Step 3: Deploy to Vercel

### Option A: Vercel Dashboard (easiest)
1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your GitHub repo
3. Vercel auto-detects the `vercel.json` config
4. Add environment variables (see Step 4)
5. Click **Deploy**

### Option B: Vercel CLI
```bash
npm i -g vercel
vercel login
vercel --prod
```

---

## Step 4: Set Environment Variables

In your Vercel project → **Settings → Environment Variables**, add:

| Variable | Value | Notes |
|---|---|---|
| `SECRET_KEY` | *(generate below)* | Must be ≥16 chars, random |
| `DATABASE_URL` | `postgresql://...` | From Neon/Supabase |
| `PAYSTACK_PUBLIC_KEY` | `pk_live_xxx` or `pk_test_xxx` | From Paystack dashboard |
| `PAYSTACK_SECRET_KEY` | `sk_live_xxx` or `sk_test_xxx` | From Paystack dashboard |
| `FLASK_ENV` | `production` | Already set in vercel.json |
| `SITE_URL` | `https://your-app.vercel.app` | Your deployed URL |

### Generate a secure SECRET_KEY:
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

> [!IMPORTANT]
> Never commit real API keys to git. Use `.env` for local dev and Vercel environment variables for production.

---

## Step 5: Configure Paystack Webhook

After deployment:

1. Go to [dashboard.paystack.com](https://dashboard.paystack.com) → **Settings → API Keys & Webhooks**
2. Set the **Webhook URL** to:
   ```
   https://your-app.vercel.app/webhooks/paystack
   ```
3. Paystack will send `charge.success` events here when payments complete

---

## Step 6: Verify Deployment

1. Visit `https://your-app.vercel.app` — you should see the Bookish homepage
2. Browse the shop, add books to cart
3. Test a checkout:
   - **Test mode**: Use Paystack test card `4084 0840 8408 4081`, expiry any future date, CVV `408`
   - **Live mode**: Use a real card (KES will be charged)
4. Log in with demo accounts:
   - Customer: `jane@example.com` / `secret123`
   - Admin: `admin@bookish.co` / `admin123`
5. Check the admin dashboard at `/admin`

---

## Project Structure (key Vercel files)

```
bookish/
├── api/
│   └── index.py          ← Vercel serverless entry point
├── app/
│   ├── static/           ← CSS, images (served by @vercel/static)
│   ├── templates/        ← Jinja2 templates
│   └── ...               ← Flask app code
├── vercel.json           ← Build & routing config
├── runtime.txt           ← Python 3.12 for Vercel
├── .vercelignore         ← Files excluded from deployment
├── requirements.txt      ← Python dependencies
└── setup_prod_db.py      ← One-time DB setup script
```

---

## Troubleshooting

| Issue | Fix |
|---|---|
| **500 errors on deploy** | Check Vercel Function Logs for the actual error. Most common: missing env vars. |
| **CSS/images not loading** | Verify `vercel.json` routes serve `/static/*` correctly. |
| **"PRODUCTION ERROR: SECRET_KEY..."** | Set `SECRET_KEY` in Vercel environment variables. |
| **Database connection errors** | Check `DATABASE_URL` is correct and the database allows connections from Vercel's IPs. |
| **Paystack payments fail** | Ensure `PAYSTACK_SECRET_KEY` is set. Use test keys for sandbox mode. |
| **`postgres://` prefix error** | The config auto-converts `postgres://` → `postgresql://` for SQLAlchemy compatibility. |

> [!NOTE]
> Flask-Migrate won't run on Vercel serverless. Always run database migrations locally against the production DB using `setup_prod_db.py` or `python -m flask db upgrade`.
