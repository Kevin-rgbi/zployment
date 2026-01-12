# Deployment (Firebase Hosting -> Cloud Run)

NOTE (assumptions)
- Run these commands from the `genz-labor-market/` folder.
- Streamlit entrypoint is `streamlit_app.py`.
- Cloud Run service: `genz-dashboard` in `us-central1`.
- Firebase project id: `gen-z-labor-market-dashboard`.
- Cloud Run/Firebase may require billing enabled on the Google Cloud project.

## 0) Prereqs

- Install and initialize the gcloud CLI: https://cloud.google.com/sdk/docs/install
- Install Node.js (for Firebase CLI): https://nodejs.org/
- Install Firebase CLI:

```bash
npm install -g firebase-tools
```

## 1) Authenticate + select project

```bash
gcloud auth login
gcloud config set project gen-z-labor-market-dashboard
```

(Optional, recommended)

```bash
gcloud config set run/region us-central1
```

## 2) Enable required APIs

```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com
```

## 3) Deploy to Cloud Run (from source)

This uses Cloud Build to build the container from the Dockerfile and deploy it.

```bash
gcloud run deploy genz-dashboard \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

Verify the Cloud Run URL:

```bash
gcloud run services describe genz-dashboard \
  --region us-central1 \
  --format='value(status.url)'
```

Open the URL in a browser, or:

```bash
curl -I "$(gcloud run services describe genz-dashboard --region us-central1 --format='value(status.url)')"
```

## 4) Configure Firebase Hosting (front door)

If you have not initialized Firebase Hosting in this folder yet:

```bash
firebase login
firebase use --add gen-z-labor-market-dashboard

# If you run init, select Hosting and choose:
# - Use an existing project: gen-z-labor-market-dashboard
# - Public directory: public
# - Configure as a single-page app: No (rewrites handle routing)
# - Set up automatic builds/deploys with GitHub: No
firebase init hosting
```

This repo supports two Hosting modes:

- **Static placeholder** (no Cloud Run): uses `firebase.json` and will serve `public/index.html`.
- **Hosting → Cloud Run** (recommended for Streamlit): uses `firebase.cloudrun.json` and proxies all routes to the Cloud Run service.

Deploy Hosting (static placeholder):

```bash
firebase deploy --only hosting
```

Deploy Hosting (proxy to Cloud Run):

```bash
firebase deploy --only hosting --config firebase.cloudrun.json
```

## 5) Verify end-to-end

- Open your Firebase Hosting URL:
  - Firebase console → Hosting → your live URL
- Confirm it loads the Streamlit app (not the placeholder "Loading…" page).

## Troubleshooting

### App doesn’t start on Cloud Run
- Check Cloud Run logs:

```bash
gcloud run services logs read genz-dashboard --region us-central1 --limit 100
```

Common causes:
- Missing `PORT` binding (this repo runs Streamlit with `--server.port=$PORT` in the Dockerfile).
- Missing data file `data/processed/monthly_labor_market_features.csv` (ensure it’s present in the image build context).

### Firebase Hosting shows only the placeholder page
- The rewrite may not be deployed or the project may be wrong.

```bash
firebase projects:list
firebase use gen-z-labor-market-dashboard
firebase deploy --only hosting
```

### 403 / permission issues
- Ensure Cloud Run service allows unauthenticated access:

```bash
gcloud run services add-iam-policy-binding genz-dashboard \
  --region us-central1 \
  --member="allUsers" \
  --role="roles/run.invoker"
```

### WebSocket / Streamlit connectivity issues
- Streamlit relies on WebSockets; Firebase Hosting rewrites to Cloud Run should support this.
- If the UI loads but charts don’t update, inspect browser devtools network for blocked requests to `/_stcore/*`.
