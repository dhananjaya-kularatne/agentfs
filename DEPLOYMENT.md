# Deployment

AgentFS deploys as three pieces:

| Piece | Host | Notes |
|---|---|---|
| Database | MongoDB Atlas (M0, free) | Session + step history |
| Backend | Railway (Docker) | FastAPI, one instance |
| Frontend | Vercel (static Vite build) | Talks to the backend over HTTPS |

The order matters: **Atlas → Railway → Vercel → connect the two**. You need a
Groq API key that can call a tool-calling model before you start.

---

## 1. MongoDB Atlas

1. Create an account at <https://www.mongodb.com/cloud/atlas/register>.
2. **Create a cluster** → choose **M0** (free), any provider/region near your
   Railway region. Name it e.g. `agentfs`.
3. **Database Access** → *Add New Database User* → username/password auth (e.g.
   user `agentfs`, a generated password). Save the password.
4. **Network Access** → *Add IP Address* → **Allow access from anywhere**
   (`0.0.0.0/0`). Railway does not publish a fixed egress IP on the trial/hobby
   plans, so an allowlist entry per IP is not practical here.
5. **Clusters** → *Connect* → *Drivers* → copy the connection string. It looks
   like:
   ```
   mongodb+srv://agentfs:<password>@agentfs.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
   Replace `<password>` with the real password. This is your `MONGODB_URI`.

The database name defaults to `agentfs` (see `MONGODB_DB_NAME`); the driver
creates it and the `sessions` collection on first write.

---

## 2. Backend on Railway

1. Sign in at <https://railway.app> with GitHub.
2. **New Project** → *Deploy from GitHub repo* → pick this repo.
3. Open the service → **Settings**:
   - **Root Directory**: `backend`
     (so Railway uses `backend/Dockerfile` and `backend/railway.toml`).
   - Build/deploy settings come from `railway.toml` — Docker builder,
     health check on `/health`. Nothing to type.
4. **Variables** → add:

   | Variable | Value |
   |---|---|
   | `GROQ_API_KEY` | your Groq key |
   | `MONGODB_URI` | the Atlas string from step 1 |
   | `ALLOWED_ORIGINS` | leave blank for now — set in step 4 |
   | `GROQ_MODEL` | *(optional)* defaults to `openai/gpt-oss-120b` |

   `MONGODB_DB_NAME`, `AGENT_WORKING_DIRECTORY`, and the `RATE_LIMIT_*` values
   all have working defaults and can be omitted.
5. **Deploy**. Watch the build logs; the health check must go green.
6. **Settings → Networking → Generate Domain**. You get something like
   `https://agentfs-backend-production.up.railway.app`. Confirm:
   - `<domain>/health` → `{"status":"AgentFS API is running"}`
   - `<domain>/docs` → Swagger UI

---

## 3. Frontend on Vercel

1. Sign in at <https://vercel.com> with GitHub.
2. **Add New… → Project** → import this repo.
3. Configure:
   - **Root Directory**: `frontend`
   - Framework preset: **Vite** (auto-detected; `frontend/vercel.json` pins it).
4. **Environment Variables** → add:

   | Name | Value |
   |---|---|
   | `VITE_API_BASE_URL` | your Railway domain, **no trailing slash** |

5. **Deploy**. You get `https://<project>.vercel.app`.

`VITE_API_BASE_URL` is read at build time and baked into the bundle, so if you
change it later you must redeploy the frontend.

---

## 4. Connect them (CORS)

1. Back in **Railway → Variables**, set:
   ```
   ALLOWED_ORIGINS = https://<project>.vercel.app
   ```
   (comma-separate if you have more than one origin; no trailing slash).
2. Railway redeploys the backend automatically.
3. Open the Vercel URL, run a task, approve a destructive action. Watch
   Railway's logs for the request.

Vercel preview deployments use per-commit subdomains that won't be in
`ALLOWED_ORIGINS`. If you want previews to work against the live backend, set
`ALLOWED_ORIGINS` to include them or switch `main.py` to
`allow_origin_regex=r"https://.*\.vercel\.app"` (more permissive — only do this
for a throwaway demo).

---

## Operational notes

- **Single instance only.** The rate limiter (`app/services/rate_limiter.py`)
  and its per-client counters live in process memory. Do not scale the Railway
  service beyond one replica — a second replica would have its own separate
  budget and the limit would effectively double.
- **The sandbox filesystem is ephemeral.** `AGENT_WORKING_DIRECTORY` resolves to
  `/app/sandbox` inside the container and is wiped on every redeploy or restart.
  Each client's folder is re-seeded with the sample files on their next request,
  so this is fine for a demo. To keep files across deploys, attach a Railway
  **Volume** mounted at `/app/sandbox`.
- **Per-client folders are never cleaned up.** Every unique `X-Client-Id`
  creates a directory and a MongoDB document that persist (until the next
  redeploy, for the files). Not a problem at demo traffic; a real deployment
  would add a TTL index on `sessions` and a sandbox reaper.
- **Cold starts / cost.** Railway's trial gives a fixed credit that the running
  service consumes over time; the Hobby plan is a small monthly fee. Atlas M0
  and Vercel Hobby are free. The Groq endpoint is unauthenticated and
  rate-limited only by the spoofable client ID, so anyone can spend your Groq
  quota — keep an eye on Groq usage, or add an IP-based limit / a global cap if
  the demo gets attention.
- **Secrets.** `GROQ_API_KEY` and `MONGODB_URI` only ever live in Railway's
  variable store. Never commit a real `.env`.

---

## Local full-stack sanity check (Docker)

To run the backend container the way Railway will:

```bash
cd backend
docker build -t agentfs-backend .
docker run --rm -p 8000:8000 \
  -e GROQ_API_KEY=... \
  -e MONGODB_URI="mongodb+srv://..." \
  -e ALLOWED_ORIGINS=http://localhost:5173 \
  agentfs-backend
```

Then run the frontend against it with `VITE_API_BASE_URL=http://localhost:8000
npm run dev` in `frontend/`.
