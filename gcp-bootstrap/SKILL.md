---
name: gcp-bootstrap
description: >
  Bootstrap a Google Cloud-backed project: authenticate, enable APIs, set up
  Secret Manager, scaffold config validation, and generate .env.example.
  Use when starting a new GCP project, adding Google Cloud to an existing project,
  or when the user says "set up GCP", "bootstrap google cloud", "configure cloud auth",
  or "add Secret Manager". Works for Python (FastAPI) and TypeScript (Express/Node) stacks.
argument-hint: [python|typescript]
disable-model-invocation: true
---

# GCP Bootstrap — Google Cloud Project Setup

Bootstrap a Google Cloud-backed project with proper auth, secrets, and config validation.
Stack is determined by `$ARGUMENTS` or auto-detected from `package.json` / `requirements.txt`.

## Step 1: Detect Stack

Check for `package.json` (TypeScript/Node) or `requirements.txt` / `pyproject.toml` (Python).
If `$ARGUMENTS` is provided, use that. Otherwise auto-detect.

## Step 2: Authenticate

Verify GCP authentication is in place:

```bash
# Check if already authenticated
gcloud auth application-default print-access-token > /dev/null 2>&1
```

If not authenticated, instruct the user:
```
Please run: ! gcloud auth application-default login
```

Verify project is set:
```bash
gcloud config get-value project
```

If no project, ask user for project ID and set it:
```bash
gcloud config set project <PROJECT_ID>
```

## Step 3: Enable Required APIs

Ask the user which Google Cloud services they need. Common combinations:

| Use Case | APIs to Enable |
|----------|---------------|
| AI/LLM (Gemini) | `aiplatform.googleapis.com` |
| Speech-to-Text | `speech.googleapis.com` |
| Cloud Storage | `storage.googleapis.com` |
| Secret Manager | `secretmanager.googleapis.com` |
| Gmail/Drive/Sheets | OAuth2 — no API enablement needed, but `gmail.googleapis.com`, `drive.googleapis.com`, `sheets.googleapis.com` |
| Firebase | `firebase.googleapis.com`, `firestore.googleapis.com` |

```bash
gcloud services enable <api1> <api2> --project=<PROJECT_ID>
```

## Step 4: Set Up Secret Manager

If the project needs API keys or sensitive config:

```bash
# Create a secret
echo -n "<value>" | gcloud secrets create <SECRET_NAME> --data-file=- --project=<PROJECT_ID>

# Grant access to the default compute service account
gcloud secrets add-iam-policy-binding <SECRET_NAME> \
  --member="serviceAccount:<PROJECT_NUMBER>-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project=<PROJECT_ID>
```

Common secrets: `GEMINI_API_KEY`, `GOOGLE_CLIENT_SECRET`, database credentials.

## Step 5: Scaffold Config Validation

### Python (Pydantic Settings)

Create `utils/config.py`:

```python
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    google_cloud_project: str
    gemini_api_key: str
    gcs_bucket_name: str = ""

    # Optional: fetch from Secret Manager at startup
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

Add to `requirements.txt`:
```
pydantic-settings>=2.0
google-cloud-secret-manager>=2.21.0
```

### TypeScript (Node/Express)

Create `src/config.ts`:

```typescript
import { SecretManagerServiceClient } from '@google-cloud/secret-manager';

interface Config {
  googleCloudProject: string;
  geminiApiKey: string;
  gcsBucketName: string;
  googleClientId: string;
  googleClientSecret: string;
  googleRedirectUri: string;
  appUrl: string;
}

function requireEnv(key: string): string {
  const value = process.env[key];
  if (!value) throw new Error(`Missing required env var: ${key}`);
  return value;
}

export const config: Config = {
  googleCloudProject: requireEnv('GOOGLE_CLOUD_PROJECT'),
  geminiApiKey: requireEnv('GEMINI_API_KEY'),
  gcsBucketName: process.env.GCS_BUCKET_NAME || '',
  googleClientId: requireEnv('GOOGLE_CLIENT_ID'),
  googleClientSecret: requireEnv('GOOGLE_CLIENT_SECRET'),
  googleRedirectUri: requireEnv('GOOGLE_REDIRECT_URI'),
  appUrl: requireEnv('APP_URL'),
};
```

## Step 6: Generate .env Files

Create `.env.example` with all required variables (no values):

```bash
# Google Cloud
GOOGLE_CLOUD_PROJECT=
GCS_BUCKET_NAME=

# Gemini AI
GEMINI_API_KEY=

# OAuth2 (if web app)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=http://localhost:3000/api/auth/callback
APP_URL=http://localhost:3000
```

Create `.env` from `.env.example` if it doesn't exist. Ask user for values.

## Step 7: Update .gitignore

Ensure these are ignored:
```
.env
credentials.json
*.key
token.json
service-account-key.json
```

## Step 8: Verify

Run a quick smoke test:

### Python
```python
from utils.config import settings
print(f"Project: {settings.google_cloud_project}")
```

### TypeScript
```typescript
import { config } from './src/config';
console.log(`Project: ${config.googleCloudProject}`);
```

## Reference: Common GCP Patterns

See [references/gcp-patterns.md](references/gcp-patterns.md) for OAuth2 flow setup,
GCS upload patterns, and Secret Manager runtime access patterns.
