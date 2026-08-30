# Google Cloud Setup for internly

This guide walks you through setting up Gmail API access so internly can send emails through your Gmail account.

## Step 1: Create a Google Cloud Project

1. Go to **https://console.cloud.google.com/**
2. Click the project dropdown at the top (next to the Google Cloud logo)
3. Click **New Project**
4. Enter a project name: `internly-gmail`
5. Click **Create**
6. Wait for it to finish, then select it from the dropdown

## Step 2: Enable APIs

Open these URLs one by one and click **Enable**:

1. **Gmail API**: https://console.cloud.google.com/flows/enableapi?apiid=gmail.googleapis.com
2. **Gmail MCP API**: https://console.cloud.google.com/flows/enableapi?apiid=gmailmcp.googleapis.com

Or run in terminal (if you have `gcloud` CLI installed):
```bash
gcloud services enable gmail.googleapis.com gmailmcp.googleapis.com --project=internly-gmail
```

## Step 3: Configure OAuth Consent Screen

1. Go to https://console.cloud.google.com/auth/branding
2. Click **Get Started** (if first time)
3. Fill in:
   - **App name**: `internly`
   - **User support email**: your email address
4. Click **Next**
5. Under **Audience**, select **External** (unless you have Google Workspace)
6. Click **Next**
7. Under **Contact Information**, enter your email
8. Click **Next**
9. Check **I agree** → **Continue** → **Create**

## Step 4: Add Yourself as Test User

1. Go to https://console.cloud.google.com/auth/audience
2. Under **Test users**, click **Add users**
3. Enter your Gmail address (the one you want to send from)
4. Click **Save**

## Step 5: Add OAuth Scopes

1. Go to https://console.cloud.google.com/auth/scopes
2. Click **Add or Remove Scopes**
3. Paste these one at a time and click **Add to Table**:
   ```
   https://www.googleapis.com/auth/gmail.readonly
   https://www.googleapis.com/auth/gmail.compose
   ```
4. Click **Update** → **Save**

## Step 6: Create OAuth Credentials

1. Go to https://console.cloud.google.com/auth/clients/create
2. **Application type**: `Web application`
3. **Name**: `internly-mcp`
4. Under **Authorized redirect URIs** → click **+ Add URI**:
   ```
   https://developers.google.com/oauthplayground
   ```
5. Click **Create**
6. Copy your **Client ID** and **Client Secret** — save them somewhere safe

## Step 7: Get a Refresh Token

1. Go to https://developers.google.com/oauthplayground
2. Click the **gear icon** (top right)
3. Check **Use your own OAuth credentials**
4. Enter your **Client ID** and **Client Secret**
5. In the left panel, find and check:
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/gmail.compose`
6. Click **Authorize APIs** → sign in with your Google account → grant access
7. Click **Exchange authorization code for tokens**
8. Copy the **Refresh token** value

## Step 8: Connect to OpenCode

### Option A: Environment Variables (Recommended)

Set these in PowerShell:
```powershell
[System.Environment]::SetEnvironmentVariable("GOOGLE_GMAIL_CLIENT_ID", "YOUR_CLIENT_ID", "User")
[System.Environment]::SetEnvironmentVariable("GOOGLE_GMAIL_CLIENT_SECRET", "YOUR_CLIENT_SECRET", "User")
```

### Option B: Add to OpenCode Config

Edit `C:\Users\krish\.config\opencode\opencode.jsonc` and add to the `mcp` section:

```jsonc
"gmail": {
  "type": "remote",
  "url": "https://gmailmcp.googleapis.com/mcp/v1",
  "oauth": {
    "clientId": "{env:GOOGLE_GMAIL_CLIENT_ID}",
    "clientSecret": "{env:GOOGLE_GMAIL_CLIENT_SECRET}"
  }
}
```

## Step 9: Test It

Restart OpenCode, then test by running:
```
internly.py stats
```

Or test the Gmail connection directly:
```
Search my Gmail for recent emails. use gmail
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Gmail API not enabled" | Make sure you enabled BOTH gmail.googleapis.com AND gmailmcp.googleapis.com |
| "Token expired" | Tokens for External apps expire after 7 days. Re-do Step 7, or publish your app |
| "Access denied" | Make sure you added your email as a test user in Step 4 |
| "OAuth consent screen" | Make sure you added the scopes in Step 5 |
| "MCP tools not showing" | Restart OpenCode after changing opencode.jsonc |

## Important Notes

- **External apps**: Tokens expire after 7 days. You'll need to re-authenticate weekly unless you publish the app (which requires Google verification).
- **Sending limits**: Gmail allows 500 emails/day for regular accounts, 2000/day for Workspace. internly defaults to 25/day to stay safe.
- **Spam risk**: If too many people mark your emails as spam, Gmail may restrict your account. Start slow (10-15/day) and scale up.
