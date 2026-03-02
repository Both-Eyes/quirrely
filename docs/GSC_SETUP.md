# Google Search Console Integration Guide

## Overview

This guide explains how to connect your Google Search Console data to the LNCP optimization system.

## Prerequisites

1. **Google Cloud Project** with Search Console API enabled
2. **Service Account** with appropriate permissions
3. **Site verified** in Google Search Console
4. **Python dependencies** installed

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Note your Project ID

## Step 2: Enable Search Console API

1. Go to **APIs & Services** → **Library**
2. Search for "Google Search Console API"
3. Click **Enable**

## Step 3: Create Service Account

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **Service Account**
3. Fill in details:
   - Name: `lncp-gsc-reader`
   - Description: `LNCP Search Console data reader`
4. Grant role: **No role needed** (we'll use domain-wide delegation)
5. Click **Done**

## Step 4: Create Service Account Key

1. Click on your new service account
2. Go to **Keys** tab
3. Click **Add Key** → **Create new key**
4. Choose **JSON** format
5. Download the file
6. Save as `credentials/gsc-service-account.json`

## Step 5: Add Service Account to Search Console

1. Go to [Google Search Console](https://search.google.com/search-console)
2. Select your property
3. Go to **Settings** → **Users and permissions**
4. Click **Add user**
5. Enter the service account email (from the JSON file: `client_email`)
6. Set permission to **Full** or **Restricted**
7. Click **Add**

## Step 6: Install Dependencies

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## Step 7: Configure Environment

Set environment variables:

```bash
export GSC_CREDENTIALS_PATH=/path/to/credentials/gsc-service-account.json
export GSC_SITE_URL=https://quirrely.io
```

Or create a `.env` file:

```
GSC_CREDENTIALS_PATH=credentials/gsc-service-account.json
GSC_SITE_URL=https://quirrely.io
```

## Step 8: Test Connection

```python
from lncp.meta.blog.gsc_real import check_gsc_credentials

# Check credentials
result = check_gsc_credentials()
print(result)

# If successful, fetch data
from lncp.meta.blog import fetch_gsc_data

data = fetch_gsc_data(
    site_url="https://quirrely.io",
    days=28,
    use_simulator=False,  # Use real API
)

print(f"Total impressions: {data.total_metrics.impressions}")
print(f"Total clicks: {data.total_metrics.clicks}")
print(f"Pages tracked: {len(data.pages)}")
```

## Usage in LNCP

Once configured, update the unified orchestrator:

```python
from lncp.meta import get_unified_orchestrator

orchestrator = get_unified_orchestrator()

# Enable real GSC data
orchestrator.gsc_enabled = True
orchestrator.gsc_use_simulator = False  # Use real API

# Run cycle
result = orchestrator.run_cycle(force=True)
```

## Troubleshooting

### "Authentication failed"

- Verify the JSON file is valid
- Check the `client_email` has access to your Search Console property
- Ensure the API is enabled in your Google Cloud project

### "No data returned"

- GSC has a 2-day data delay
- New properties may take time to accumulate data
- Verify the site URL matches exactly (including https://)

### "Permission denied"

- The service account needs at least "Restricted" access in Search Console
- Double-check the email address was added correctly

### "API not enabled"

- Go to Google Cloud Console
- Enable the "Google Search Console API"

## Security Notes

1. **Keep credentials secure** - Never commit JSON to git
2. **Use least privilege** - Restricted access is sufficient for reading
3. **Rotate keys periodically** - Delete old keys and create new ones
4. **Monitor usage** - Check API quotas in Google Cloud Console

## API Limits

- **Requests per day**: 25,000
- **Requests per minute**: 1,200
- **Rows per request**: 25,000

The LNCP client handles pagination automatically.

## File Structure

```
lncp-web-app/
├── credentials/
│   └── gsc-service-account.json  # Your credentials (git-ignored)
├── lncp/
│   └── meta/
│       └── blog/
│           ├── gsc.py           # Main GSC module
│           └── gsc_real.py      # Real API client
└── .env                          # Environment variables
```

## Sample Credentials Format

Your `gsc-service-account.json` should look like:

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "lncp-gsc-reader@your-project-id.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "..."
}
```

## Next Steps

1. Set up credentials following this guide
2. Test with `check_gsc_credentials()`
3. Run a test fetch with `fetch_gsc_data(use_simulator=False)`
4. Configure the orchestrator to use real data
5. Set up cron job for automatic cycles (see P5)
