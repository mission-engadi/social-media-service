# Buffer Integration Guide

## Overview
This service integrates with Buffer API to schedule and manage social media posts across multiple platforms.

## Prerequisites
1. Buffer account (https://buffer.com)
2. Buffer API access token
3. Connected social media profiles in Buffer

---

## Step 1: Create Buffer Account

1. Visit https://buffer.com
2. Sign up or log in
3. Connect your social media accounts:
   - Twitter/X
   - Facebook
   - LinkedIn
   - Instagram
   - TikTok

---

## Step 2: Get Buffer API Access Token

### Option A: Using Buffer's Developer Portal

1. Visit https://publish.buffer.com/profile
2. Go to **Settings** → **API**
3. Click **Create New Access Token**
4. Copy the access token

### Option B: OAuth Flow (Production)

For production applications, implement OAuth 2.0:

1. Register your app at https://buffer.com/developers
2. Get your Client ID and Client Secret
3. Implement OAuth flow:
   ```
   https://bufferapp.com/oauth2/authorize?
     client_id=YOUR_CLIENT_ID&
     redirect_uri=YOUR_REDIRECT_URI&
     response_type=code
   ```
4. Exchange authorization code for access token

---

## Step 3: Configure Service

### Environment Variables

Add to `.env` file:

```bash
# Buffer Configuration
BUFFER_API_URL=https://api.bufferapp.com/1
BUFFER_ACCESS_TOKEN=your_buffer_access_token_here
```

### Test Configuration

```bash
# Start the service
./start.sh

# Test Buffer connection
curl -X GET "http://localhost:8007/api/v1/buffer/profiles" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Step 4: Connect Social Accounts

### Create Social Account in Service

```bash
curl -X POST "http://localhost:8007/api/v1/social-accounts" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "twitter",
    "account_name": "@yourusername",
    "buffer_profile_id": "BUFFER_PROFILE_ID",
    "access_token": "BUFFER_ACCESS_TOKEN"
  }'
```

### Get Buffer Profile IDs

```bash
curl -X GET "http://localhost:8007/api/v1/buffer/profiles" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

Response:
```json
[
  {
    "id": "5f7c8b9a1e4f3a0001234567",
    "service": "twitter",
    "formatted_service": "Twitter",
    "formatted_username": "@yourusername"
  }
]
```

---

## Step 5: Schedule Posts

### Create Draft Post

```bash
curl -X POST "http://localhost:8007/api/v1/posts" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "social_account_id": 1,
    "content": "Hello from Social Media Service! 🚀",
    "scheduled_time": "2025-12-25T10:00:00",
    "platform": "twitter"
  }'
```

### Schedule via Buffer

```bash
curl -X POST "http://localhost:8007/api/v1/posts/1/schedule" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Buffer API Features Used

### 1. Get User Profile
```
GET /user.json?access_token=TOKEN
```

### 2. Get Profiles (Social Accounts)
```
GET /profiles.json?access_token=TOKEN
```

### 3. Create Update (Post)
```
POST /updates/create.json
{
  "profile_ids": ["PROFILE_ID"],
  "text": "Post content",
  "scheduled_at": 1640433600,
  "media": {"photo": "https://example.com/image.jpg"}
}
```

### 4. Get Update Statistics
```
GET /updates/{id}/statistics.json?access_token=TOKEN
```

---

## Platform-Specific Notes

### Twitter/X
- Character limit: 280
- Supports images, GIFs, videos
- Hashtags recommended

### Facebook
- Character limit: 63,206 (but shorter is better)
- Supports links, images, videos
- Best times: 1-4 PM weekdays

### LinkedIn
- Character limit: 3,000
- Professional tone
- Best times: Tuesday-Thursday, 7-8 AM

### Instagram
- Requires image/video
- Character limit: 2,200
- First comment can include additional hashtags

---

## Error Handling

### Common Errors

**401 Unauthorized**
```json
{"error": "Unauthorized", "message": "Invalid access token"}
```
**Solution:** Refresh your Buffer access token

**403 Forbidden**
```json
{"error": "Forbidden", "message": "Profile not accessible"}
```
**Solution:** Reconnect the social account in Buffer

**503 Service Unavailable**
```json
{"error": "Buffer API unavailable"}
```
**Solution:** Wait and retry, Buffer may be experiencing issues

---

## Rate Limits

- **Buffer API**: 60 requests per minute per access token
- **Service handles**: Automatic retry with exponential backoff
- **Best practice**: Cache Buffer profile data

---

## Security Best Practices

1. **Never commit tokens** to version control
2. **Use environment variables** for sensitive data
3. **Rotate tokens regularly** (every 90 days)
4. **Use OAuth in production** instead of personal access tokens
5. **Implement token encryption** in database

---

## Testing

### Test Buffer Connection
```bash
pytest tests/test_buffer_integration.py -v
```

### Manual Testing
```bash
# Get profiles
curl https://api.bufferapp.com/1/profiles.json?access_token=YOUR_TOKEN

# Test authentication
curl https://api.bufferapp.com/1/user.json?access_token=YOUR_TOKEN
```

---

## Troubleshooting

### Issue: "Buffer profile not found"
**Solution:** Sync profiles using `/social-accounts/{id}/sync-buffer`

### Issue: "Post scheduling failed"
**Checks:**
1. Verify Buffer access token is valid
2. Check social account is connected in Buffer
3. Ensure scheduled time is in the future
4. Verify content meets platform requirements

### Issue: "Analytics not syncing"
**Solution:** Use `/analytics/sync` endpoint to manually trigger sync

---

## Resources

- **Buffer API Docs**: https://buffer.com/developers/api
- **Buffer Status**: https://status.buffer.com
- **Support**: https://support.buffer.com

---

## Next Steps

1. ✅ Create Buffer account and get access token
2. ✅ Configure service with Buffer credentials
3. ✅ Connect social accounts
4. ✅ Test post scheduling
5. ✅ Monitor analytics
6. 🚀 Start scheduling posts!
