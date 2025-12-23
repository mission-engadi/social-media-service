# Social Media Service - API Documentation

## Base URL
```
http://localhost:8007/api/v1
```

## Authentication
All endpoints require JWT authentication via Bearer token:
```
Authorization: Bearer <your-jwt-token>
```

---

## 📱 Social Accounts API

### 1. Create Social Account
**POST** `/social-accounts`

Connect a new social media account.

**Request Body:**
```json
{
  "platform": "twitter",
  "account_name": "@username",
  "buffer_profile_id": "buf_123",
  "access_token": "token_123"
}
```

### 2. Get Social Account
**GET** `/social-accounts/{id}`

### 3. List Social Accounts
**GET** `/social-accounts`

### 4. Update Social Account
**PUT** `/social-accounts/{id}`

### 5. Delete Social Account
**DELETE** `/social-accounts/{id}`

### 6. Test Connection
**POST** `/social-accounts/{id}/test-connection`

### 7. Sync with Buffer
**POST** `/social-accounts/{id}/sync-buffer`

---

## 📝 Scheduled Posts API

### 8. Create Scheduled Post
**POST** `/posts`

**Request Body:**
```json
{
  "social_account_id": 1,
  "campaign_id": 1,
  "content": "Post content #hashtag",
  "scheduled_time": "2025-12-25T10:00:00",
  "platform": "twitter",
  "media_urls": ["https://example.com/image.jpg"]
}
```

### 9. Get Scheduled Post
**GET** `/posts/{id}`

### 10. List Scheduled Posts
**GET** `/posts`

**Query Parameters:**
- `status` - Filter by status (draft/scheduled/published)
- `platform` - Filter by platform
- `campaign_id` - Filter by campaign

### 11. Update Scheduled Post
**PUT** `/posts/{id}`

### 12. Delete Scheduled Post
**DELETE** `/posts/{id}`

### 13. Schedule Post via Buffer
**POST** `/posts/{id}/schedule`

Schedule a post using Buffer API.

### 14. Bulk Schedule Posts
**POST** `/posts/bulk`

**Request Body:**
```json
{
  "posts": [
    {
      "social_account_id": 1,
      "content": "Post 1",
      "scheduled_time": "2025-12-25T10:00:00"
    }
  ]
}
```

### 15. Get Content Calendar
**GET** `/posts/calendar`

**Query Parameters:**
- `start_date` - Start date (YYYY-MM-DD)
- `end_date` - End date (YYYY-MM-DD)

### 16. Cancel Scheduled Post
**POST** `/posts/{id}/cancel`

### 17. Reschedule Post
**POST** `/posts/{id}/reschedule`

---

## 📊 Post Analytics API

### 18. Record Analytics
**POST** `/analytics`

**Request Body:**
```json
{
  "post_id": 1,
  "views": 1000,
  "likes": 50,
  "shares": 10,
  "comments": 5,
  "engagement_rate": 6.5
}
```

### 19. Get Analytics
**GET** `/analytics/{id}`

### 20. List Analytics
**GET** `/analytics`

### 21. Update Analytics
**PUT** `/analytics/{id}`

### 22. Delete Analytics
**DELETE** `/analytics/{id}`

### 23. Sync Analytics from Buffer
**POST** `/analytics/sync`

Sync analytics data from Buffer for all posts.

---

## 🎯 Campaigns API

### 24. Create Campaign
**POST** `/campaigns`

**Request Body:**
```json
{
  "name": "Summer Campaign 2025",
  "description": "Summer promotion",
  "start_date": "2025-06-01",
  "end_date": "2025-08-31",
  "status": "active"
}
```

### 25. Get Campaign
**GET** `/campaigns/{id}`

### 26. List Campaigns
**GET** `/campaigns`

**Query Parameters:**
- `status` - Filter by status (active/paused/completed)

### 27. Update Campaign
**PUT** `/campaigns/{id}`

### 28. Delete Campaign
**DELETE** `/campaigns/{id}`

### 29. Get Campaign Analytics
**GET** `/campaigns/{id}/analytics`

Returns aggregated analytics for all posts in the campaign.

### 30. Get Campaign Posts
**GET** `/campaigns/{id}/posts`

List all posts belonging to a campaign.

---

## ⚙️ Buffer Configuration API

### 31. Create Buffer Config
**POST** `/buffer/config`

**Request Body:**
```json
{
  "access_token": "your-buffer-access-token"
}
```

### 32. Get Buffer Config
**GET** `/buffer/config/{id}`

### 33. Update Buffer Config
**PUT** `/buffer/config/{id}`

### 34. Delete Buffer Config
**DELETE** `/buffer/config/{id}`

### 35. Get Buffer Profiles
**GET** `/buffer/profiles`

Retrieve all connected Buffer profiles for the authenticated user.

---

## Response Format

### Success Response
```json
{
  "id": 1,
  "field": "value",
  "created_at": "2025-12-23T10:00:00",
  "updated_at": "2025-12-23T10:00:00"
}
```

### Error Response
```json
{
  "detail": "Error message"
}
```

## Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error
- `503` - Service Unavailable (Buffer API issues)

## Rate Limiting
- Follows Buffer API rate limits
- 60 requests per minute per user

## Pagination
List endpoints support pagination:
```
GET /api/v1/posts?skip=0&limit=20
```

## Interactive Documentation
Visit http://localhost:8007/docs for interactive Swagger UI.
