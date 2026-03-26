# GCP Integration Patterns Reference

Common patterns extracted from Brain, LabTranscription, and InventoryMgmt.

---

## 1. OAuth2 Flow (Web Apps)

### Express/TypeScript (from InventoryMgmt)

```typescript
import { OAuth2Client } from 'google-auth-library';

const oauth2Client = new OAuth2Client(
  process.env.GOOGLE_CLIENT_ID,
  process.env.GOOGLE_CLIENT_SECRET,
  process.env.GOOGLE_REDIRECT_URI
);

// Generate auth URL
app.get('/api/auth/url', (req, res) => {
  const url = oauth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: [
      'https://www.googleapis.com/auth/gmail.readonly',
      'https://www.googleapis.com/auth/drive.readonly',
    ],
    prompt: 'consent',
  });
  res.json({ url });
});

// Handle callback — store tokens in httpOnly cookie
app.get('/api/auth/callback', async (req, res) => {
  const { code } = req.query;
  const { tokens } = await oauth2Client.getToken(code as string);
  res.cookie('google_tokens', JSON.stringify(tokens), {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 7 * 24 * 60 * 60 * 1000,
  });
  res.redirect('/');
});
```

**Security notes:**
- Encrypt cookie values with AES-256-GCM in production
- Use `sameSite: 'lax'` minimum
- Set `secure: true` in production
- Apply OAuth middleware ONLY to routes that need Google API tokens

---

## 2. Google Cloud Storage Upload (Python)

### From LabTranscription

```python
from google.cloud import storage

def upload_to_gcs(local_path: str, bucket_name: str, blob_name: str) -> str:
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(local_path)
    return f"gs://{bucket_name}/{blob_name}"
```

### From Brain (audio files)

```python
from google.cloud import storage
import uuid

def upload_audio(file_path: str, bucket_name: str) -> str:
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob_name = f"audio/{uuid.uuid4()}/{Path(file_path).name}"
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(file_path, content_type="audio/wav")
    return blob_name
```

---

## 3. Secret Manager Runtime Access

### Python (from LabTranscription/utils/config.py pattern)

```python
from google.cloud import secretmanager

def get_secret(project_id: str, secret_id: str, version: str = "latest") -> str:
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("utf-8")
```

### Pydantic Settings with Secret Manager Fallback

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    google_cloud_project: str = ""
    gemini_api_key: str = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.gemini_api_key and self.google_cloud_project:
            self.gemini_api_key = get_secret(
                self.google_cloud_project, "GEMINI_API_KEY"
            )

    class Config:
        env_file = ".env"
```

---

## 4. Application Default Credentials (ADC)

All Google Cloud client libraries auto-discover credentials via ADC:

```bash
# For local development
gcloud auth application-default login

# For production (Cloud Run, GKE, etc.)
# ADC is automatic via the service account attached to the resource
```

**No code changes needed** between local and production — the client libraries handle it.

---

## 5. Auth Middleware Placement (Critical Pattern)

| Route needs... | Auth approach |
|----------------|---------------|
| Google API tokens (Gmail, Drive, Sheets) | Full OAuth middleware |
| Server-side API key only (Gemini, Vertex AI) | Rate limiter only |
| Public data (health, static) | No auth |

**Anti-pattern:** Applying OAuth middleware to Gemini-only routes causes 401 errors
when the user hasn't completed the OAuth flow. Gemini uses a server-side API key,
not user OAuth tokens.

---

## 6. Service Enablement Quick Reference

```bash
# AI/ML
gcloud services enable aiplatform.googleapis.com
gcloud services enable speech.googleapis.com

# Storage
gcloud services enable storage.googleapis.com
gcloud services enable secretmanager.googleapis.com

# Firebase
gcloud services enable firebase.googleapis.com
gcloud services enable firestore.googleapis.com

# Google Workspace APIs (for OAuth)
gcloud services enable gmail.googleapis.com
gcloud services enable drive.googleapis.com
gcloud services enable sheets.googleapis.com
```
