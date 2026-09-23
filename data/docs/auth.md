# Authentication

Every NimbusPay request must include an API key in the `Authorization` header as a Bearer token: `Authorization: Bearer np_live_...`. Never expose keys in client-side code; call the API from your server.

API keys can be created and revoked from the dashboard under Settings > API keys. Keys are shown once at creation — store them securely.

OAuth2 is available for platforms acting on behalf of merchants. Use the authorization code flow with redirect URI registration, then exchange the code at `POST /v1/oauth/token`. Access tokens expire after 3600 seconds; refresh tokens expire after 30 days.
